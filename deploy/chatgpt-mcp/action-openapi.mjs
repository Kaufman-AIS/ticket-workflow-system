const safeOperationId = (name) => `paca_${name.replace(/[^A-Za-z0-9_]/g, '_')}`;

const requestSchema = (schema) => {
  if (!schema || typeof schema !== 'object') {
    return { type: 'object', properties: {}, additionalProperties: true };
  }
  const copy = structuredClone(schema);
  delete copy.$schema;
  if (copy.type === 'object' && !copy.properties) copy.properties = {};
  return copy;
};

export const buildActionOpenApi = (tools = []) => {
  const paths = {};
  for (const tool of tools) {
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
      title: 'Paca GPT Actions',
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
