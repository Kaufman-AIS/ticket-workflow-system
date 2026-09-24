import crypto from 'node:crypto';

const jsonRpcError = (id, code, message, data) => ({
  jsonrpc: '2.0',
  id: id ?? null,
  error: { code, message, ...(data === undefined ? {} : { data }) },
});

const sameSecret = (provided, expected) => {
  if (typeof provided !== 'string' || typeof expected !== 'string') return false;
  const left = Buffer.from(provided);
  const right = Buffer.from(expected);
  return left.length === right.length && crypto.timingSafeEqual(left, right);
};

const send = (res, status, body) => res.status(status).json(body);

const authenticate = (req, res, token) => {
  const authorization = req.headers?.authorization ?? '';
  const provided = authorization.match(/^Bearer\s+(.+)$/i)?.[1];
  if (sameSecret(provided, token)) return true;
  res.setHeader?.('WWW-Authenticate', 'Bearer');
  send(res, 401, { error: 'unauthorized' });
  return false;
};

/** Create a GPT Action endpoint for one MCP tool with a first-class JSON body. */
export const createToolRouter = ({ token, client, toolName }) => {
  if (!token || token.length < 32) throw new Error('CHATGPT_ACTION_TOKEN must be at least 32 characters');
  if (!client) throw new Error('an MCP client is required');
  if (!toolName) throw new Error('toolName is required');

  return async (req, res) => {
    try {
      if (!authenticate(req, res, token)) return;
      const result = await client.callTool({ name: toolName, arguments: req.body ?? {} });
      return send(res, 200, result);
    } catch (error) {
      console.error(`[chatgpt-action:${toolName}] ${error?.stack ?? error}`);
      return send(res, 502, { error: 'MCP tool call failed', tool: toolName });
    }
  };
};

/**
 * Expose the connected Paca MCP tools through the small JSON-RPC shape that
 * GPT Actions can call. The returned function is also an Express middleware.
 */
export const createActionRouter = ({ token, client }) => {
  if (!token || token.length < 32) throw new Error('CHATGPT_ACTION_TOKEN must be at least 32 characters');
  if (!client) throw new Error('an MCP client is required');

  let toolsPromise;
  const availableTools = async () => {
    toolsPromise ??= client.listTools().then(({ tools = [] }) => new Set(tools.map((tool) => tool.name)));
    return toolsPromise;
  };

  const handle = async (req, res, next) => {
    try {
      if (!authenticate(req, res, token)) return;

      const request = req.body;
      if (!request || request.jsonrpc !== '2.0' || request.id === undefined || typeof request.method !== 'string') {
        return send(res, 400, jsonRpcError(request?.id, -32600, 'Invalid Request'));
      }

      if (request.method === 'list_tools') {
        return send(res, 200, { jsonrpc: '2.0', id: request.id, result: await client.listTools() });
      }

      const tools = await availableTools();
      if (!tools.has(request.method)) {
        return send(res, 200, jsonRpcError(request.id, -32601, `Unknown MCP tool: ${request.method}`));
      }

    const rawArguments = request.params ?? {};
    const toolArguments =
      rawArguments &&
      typeof rawArguments === 'object' &&
      rawArguments.params &&
      typeof rawArguments.params === 'object' &&
      Object.keys(rawArguments).length === 1
        ? rawArguments.params
        : rawArguments;

    const result = await client.callTool({
      name: request.method,
      arguments: toolArguments,
    });
      return send(res, 200, { jsonrpc: '2.0', id: request.id, result });
    } catch (error) {
      if (error?.code === -32600 || error?.code === -32601) {
        return send(res, 200, jsonRpcError(req.body?.id, error.code, error.message));
      }
      console.error(`[chatgpt-action] ${error?.stack ?? error}`);
      return send(res, 200, jsonRpcError(req.body?.id, -32603, 'MCP tool call failed'));
    }
  };

  handle.handle = (req, res, next) => void handle(req, res, next);
  return handle;
};
