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
