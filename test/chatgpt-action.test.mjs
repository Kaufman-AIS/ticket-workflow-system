import assert from 'node:assert/strict';
import test from 'node:test';
import { createActionRouter, createToolRouter } from '../deploy/chatgpt-mcp/chatgpt-action.mjs';

const ACTION_TOKEN = 'secret-token-012345678901234567890123';

const request = async (router, options) => {
  const token = Object.hasOwn(options, 'token') ? options.token : ACTION_TOKEN;
  const { body } = options;
  const response = await new Promise((resolve, reject) => {
    const req = {
      method: 'POST',
      headers: token === undefined ? {} : { authorization: `Bearer ${token ?? ACTION_TOKEN}` },
      body,
    };
    const res = {
      statusCode: 200,
      headers: {},
      status(code) { this.statusCode = code; return this; },
      setHeader(name, value) { this.headers[name.toLowerCase()] = value; },
      json(value) { resolve({ status: this.statusCode, body: value, headers: this.headers }); },
    };
    const handler = router.handle ?? router;
    handler(req, res, (error) => error ? reject(error) : resolve({ status: 404, body: null }));
  });
  return response;
};

test('rejects requests without the action bearer token', async () => {
  const router = createActionRouter({ token: ACTION_TOKEN, client: {} });
  const response = await request(router, { token: undefined, body: {} });
  assert.equal(response.status, 401);
});

test('rejects malformed JSON-RPC requests', async () => {
  const router = createActionRouter({ token: ACTION_TOKEN, client: {} });
  const response = await request(router, { body: { method: 'list_tasks' } });
  assert.equal(response.status, 400);
  assert.equal(response.body.error.code, -32600);
});

test('dispatches a known MCP tool and returns its result', async () => {
  const calls = [];
  const router = createActionRouter({
    token: ACTION_TOKEN,
    client: {
      async listTools() { return { tools: [{ name: 'list_tasks' }] }; },
      async callTool(args) { calls.push(args); return { content: [{ type: 'text', text: 'ok' }] }; },
    },
  });
  const response = await request(router, {
    body: { jsonrpc: '2.0', id: 7, method: 'list_tasks', params: { project_id: 'p1' } },
  });
  assert.equal(response.status, 200);
  assert.deepEqual(calls, [{ name: 'list_tasks', arguments: { project_id: 'p1' } }]);
  assert.deepEqual(response.body, { jsonrpc: '2.0', id: 7, result: { content: [{ type: 'text', text: 'ok' }] } });
});

test('returns a JSON-RPC method-not-found error for unknown tools', async () => {
  const router = createActionRouter({
    token: ACTION_TOKEN,
    client: { async listTools() { return { tools: [{ name: 'list_tasks' }] }; } },
  });
  const response = await request(router, {
    body: { jsonrpc: '2.0', id: 8, method: 'drop_database', params: {} },
  });
  assert.equal(response.status, 200);
  assert.equal(response.body.error.code, -32601);
});

test('unwraps GPT Actions that nest tool arguments under params.params', async () => {
  let call;
  const router = createActionRouter({
    token: ACTION_TOKEN,
    client: {
      async listTools() { return { tools: [{ name: 'list_views' }] }; },
      async callTool(args) { call = args; return { content: [] }; },
    },
  });
  const response = await request(router, {
    body: { jsonrpc: '2.0', id: 9, method: 'list_views', params: { params: { projectId: 'p1' } } },
  });
  assert.equal(response.status, 200);
  assert.deepEqual(call, { name: 'list_views', arguments: { projectId: 'p1' } });
});

test('exposes a tool as a first-class action with direct projectId input', async () => {
  let call;
  const router = createToolRouter({
    token: ACTION_TOKEN,
    toolName: 'list_views',
    client: { async callTool(args) { call = args; return { content: [{ type: 'text', text: 'ok' }] }; } },
  });
  const response = await request(router, { body: { projectId: 'p1' } });
  assert.equal(response.status, 200);
  assert.deepEqual(call, { name: 'list_views', arguments: { projectId: 'p1' } });
});
