import assert from 'node:assert/strict';
import test from 'node:test';
import { buildActionOpenApi } from '../deploy/chatgpt-mcp/action-openapi.mjs';

test('generates one explicit GPT Action for every Paca tool', () => {
  const document = buildActionOpenApi([
    {
      name: 'create_task',
      description: 'Create a task',
      inputSchema: { type: 'object', required: ['projectId', 'title'], properties: { projectId: { type: 'string' }, title: { type: 'string' } } },
    },
  ]);
  const operation = document.paths['/chatgpt/tools/create_task'].post;
  assert.equal(operation.operationId, 'paca_create_task');
  assert.deepEqual(operation.requestBody.content['application/json'].schema.required, ['projectId', 'title']);
  assert.ok(document.components.schemas.McpResult.properties.content);
});

test('can split the catalogue into importer-safe groups of at most 30 operations', () => {
  const tools = Array.from({ length: 78 }, (_, index) => ({ name: `tool_${index}`, inputSchema: { type: 'object', properties: {} } }));
  assert.equal(Object.keys(buildActionOpenApi(tools, { start: 0, limit: 30 }).paths).length, 30);
  assert.equal(Object.keys(buildActionOpenApi(tools, { start: 30, limit: 30 }).paths).length, 30);
  assert.equal(Object.keys(buildActionOpenApi(tools, { start: 60, limit: 30 }).paths).length, 18);
});

test('adds items to incomplete array schemas from Paca', () => {
  const document = buildActionOpenApi([{ name: 'create_automation', inputSchema: {
    type: 'object',
    properties: { nodes: { type: 'array' }, edges: { type: 'array' } },
  } }]);
  const properties = document.paths['/chatgpt/tools/create_automation'].post.requestBody.content['application/json'].schema.properties;
  assert.deepEqual(properties.nodes.items, { type: 'object', properties: {}, additionalProperties: true });
  assert.deepEqual(properties.edges.items, { type: 'object', properties: {}, additionalProperties: true });
});
