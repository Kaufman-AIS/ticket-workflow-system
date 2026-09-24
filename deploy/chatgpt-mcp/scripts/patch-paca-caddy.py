#!/usr/bin/env python3
"""Insert ChatGPT MCP reverse_proxy blocks into the Paca gateway Caddyfile."""
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "/opt/ticket-workflow-system/paca/caddy/Caddyfile")
text = path.read_text()
if "paca-chatgpt-mcp:8771" in text:
    if "/chatgpt/" not in text:
        marker = "\t# -- Web application (SPA) -----------------------------------------------------"
        routes = """\t# -- ChatGPT GPT Action bridge -----------------------------------------------
\thandle /chatgpt/* {
\t\treverse_proxy paca-chatgpt-mcp:8771
\t}

"""
        if marker not in text:
            raise SystemExit(f"marker not found in {path}")
        path.write_text(text.replace(marker, routes + marker, 1))
        print(f"added GPT Action routes to {path}")
    else:
        print("already patched")
    raise SystemExit(0)

marker = "\t# -- Web application (SPA) -----------------------------------------------------"
block = """\t# -- ChatGPT remote MCP (OAuth gateway) ----------------------------------------
\t#
\t# Hosted Streamable HTTP + OAuth for ChatGPT mobile/web. Upstream is the
\t# paca-chatgpt-mcp container on this compose network.
\thandle /mcp {
\t\treverse_proxy paca-chatgpt-mcp:8771 {
\t\t\tflush_interval -1
\t\t}
\t}
\thandle /.well-known/oauth-authorization-server* {
\t\treverse_proxy paca-chatgpt-mcp:8771
\t}
\thandle /.well-known/oauth-protected-resource* {
\t\treverse_proxy paca-chatgpt-mcp:8771
\t}
\thandle /authorize {
\t\treverse_proxy paca-chatgpt-mcp:8771
\t}
\thandle /token {
\t\treverse_proxy paca-chatgpt-mcp:8771
\t}
\thandle /register {
\t\treverse_proxy paca-chatgpt-mcp:8771
\t}
\thandle /healthz-mcp {
\t\trewrite * /healthz
\t\treverse_proxy paca-chatgpt-mcp:8771
\t}

"""
if marker not in text:
    raise SystemExit(f"marker not found in {path}")
path.write_text(text.replace(marker, block + marker, 1))
print(f"patched {path}")
