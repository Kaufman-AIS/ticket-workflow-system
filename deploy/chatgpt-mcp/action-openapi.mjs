const safeOperationId = (name) => `paca_${name.replace(/[^A-Za-z0-9_]/g, '_')}`;

const normalizeSchema = (schema) => {
  if (!schema || typeof schema !== 'object') {
    return { type: 'object', properties: {}, additionalProperties: true };
  }
  const copy = structuredClone(schema);
  delete copy.$schema;
  if (copy.type === 'object') {
    copy.properties ??= {};
    for (const [name, property] of Object.entries(copy.properties)) {
      copy.properties[name] = normalizeSchema(property);
    }
  }
  if (copy.type === 'array') copy.items = normalizeSchema(copy.items);
  for (const key of ['oneOf', 'anyOf', 'allOf']) {
    if (Array.isArray(copy[key])) copy[key] = copy[key].map(normalizeSchema);
  }
  return copy;
};

const requestSchema = (schema) => normalizeSchema(schema);

export const buildActionOpenApi = (tools = [], { start = 0, limit = 30, title = 'Paca GPT Actions' } = {}) => {
  const paths = {};
  for (const tool of tools.slice(start, start + limit)) {
    if (!tool?.name) continue;
    paths[`/chatgpt/tools/${encodeURIComponent(tool.name)}`] = {
      post: {
        operationId: safeOperationId(tool.name),
        summary: tool.description?.split('\n')[0]?.slice(0, 120) || `Call Paca tool ${tool.name}`,
        description: `Calls the Paca MCP tool ${tool.name}.`,
        security: [{ bearerAuth: [] }],
        requestBody: {
          required: true,
          content: { 'application/json': { schema: requestSchema(tool.inputSchema) } },
        },
        responses: {
          '200': {
            description: 'Paca MCP tool result',
            content: { 'application/json': { schema: { $ref: '#/components/schemas/McpResult' } } },
          },
          '401': { description: 'Invalid bearer token' },
        },
      },
    };
  }

  return {
    openapi: '3.1.0',
    info: {
      title,
      version: '2.0.0',
      description: 'Explicit GPT Actions generated from the live Paca MCP tool catalogue.',
    },
    servers: [{ url: 'https://paca.kaufman-ais.com' }],
    paths,
    components: {
      securitySchemes: { bearerAuth: { type: 'http', scheme: 'bearer' } },
      schemas: {
        McpResult: {
          type: 'object',
          properties: {
            content: { type: 'array', items: { type: 'object', properties: { type: { type: 'string' }, text: { type: 'string' } }, additionalProperties: true } },
            isError: { type: 'boolean' },
          },
          additionalProperties: true,
        },
      },
    },
  };
};
