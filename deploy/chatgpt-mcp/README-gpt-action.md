# Paca as a Custom GPT Action

This bridge keeps the existing remote MCP/OAuth endpoint intact and adds a
Bearer-protected GPT Action endpoint:

`https://paca.kaufman-ais.com/chatgpt/rpc`

The OpenAPI schema is available at:

`https://paca.kaufman-ais.com/chatgpt/openapi.yaml`

## Configure the GPT

1. Open ChatGPT on desktop web and edit the Custom GPT.
2. Open **Configure → Actions → Create new action**.
3. Choose **Import from URL** and paste the OpenAPI URL above.
4. Set authentication to **API key**, type **Bearer**.
5. Paste the generated `CHATGPT_ACTION_TOKEN` as the API key.
6. Save and test by asking the GPT to call `list_tools`, then read a Paca project.

The mobile ChatGPT app can use the saved GPT after it has been configured on
desktop web. The GPT Action itself is configured in the web builder.

## Protocol

The action accepts a JSON-RPC-style request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "list_tools",
  "params": {}
}
```

For a real call, replace `method` with the exact MCP tool name and put the
tool's input object in `params`. The `list_tools` result includes the complete
tool catalogue and schemas, so the GPT can discover all installed Paca and
plugin functions.
