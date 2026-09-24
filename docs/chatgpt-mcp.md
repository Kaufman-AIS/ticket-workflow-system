# ChatGPT remote MCP (Paca)

Expose `@paca-ai/paca-mcp` to ChatGPT Web via Streamable HTTP + OAuth 2.1.

```text
  ChatGPT Web
  --HTTPS-->  https://paca.kaufman-ais.com/mcp
  --Caddy-->  paca-chatgpt-mcp:8771   (OAuth gateway)
  --proxy-->  mcp-proxy:8770
  --stdio-->  @paca-ai/paca-mcp
  --REST-->   Paca API
```

Gateway adapted from the MIT
[chatgpt-mcp-connect oauth-gateway](https://github.com/yoruuuchan/chatgpt-mcp-connect/tree/main/templates/oauth-gateway).

## Status on Hostinger

Already live:

| Check | Expect |
| --- | --- |
| `https://paca.kaufman-ais.com/healthz-mcp` | `{"ok":true,...}` |
| `https://paca.kaufman-ais.com/mcp` | HTTP **401** without OAuth |
| `https://paca.kaufman-ais.com/.well-known/oauth-authorization-server` | JSON issuer metadata |

Container: `paca-chatgpt-mcp` on Docker network `paca_default`.  
Caddy routes are patched into `/opt/ticket-workflow-system/paca/caddy/Caddyfile`.

## Connect ChatGPT

1. Open **ChatGPT on the web** (paid plan with Developer Mode / custom MCP apps).
2. **Settings → Apps → Advanced → Developer mode** (enable).
3. **Create app** / connector.
4. MCP server URL: **`https://paca.kaufman-ais.com/mcp`**
5. Authentication: **OAuth**
6. On the consent screen, paste the **OWNER_TOKEN** from the VPS:

   ```bash
   ssh deploy@187.124.175.57 'grep ^OWNER_TOKEN= /opt/ticket-workflow-system/chatgpt-mcp/.env'
   ```

7. New chat → attach the Paca app → try: “List my Paca projects.”
8. Custom MCP apps are currently supported in ChatGPT Web, not the native mobile app.

## Redeploy / restart

```bash
ssh deploy@187.124.175.57
bash /opt/ticket-workflow-system/chatgpt-mcp/scripts/deploy-on-vps.sh
```

Logs:

```bash
docker logs -f paca-chatgpt-mcp
```

## Security

- `OWNER_TOKEN` is a single-user root password for the connector.
- `PACA_API_KEY` stays on the VPS; ChatGPT never sees it.
- Prefer a dedicated Paca API key; rotate if leaked.
- Container memory limited to 512m.

## Files

| Path | Role |
| --- | --- |
| `deploy/chatgpt-mcp/` | Gateway, entrypoint, deploy scripts |
| `deploy/nginx/paca.kaufman-ais.com.conf` | Optional host-nginx routes (needs `sudo nginx reload`) |
| `docs/chatgpt-mcp.md` | This guide |
