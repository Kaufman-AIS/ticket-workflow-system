#!/usr/bin/env python3
"""Insert ChatGPT MCP reverse_proxy blocks into the Paca gateway Caddyfile."""
from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "/opt/ticket-workflow-system/paca/caddy/Caddyfile")
text = path.read_text()

if "handle @discovery_score" not in text:
    marker = "\t# -- ChatGPT remote MCP (OAuth gateway) ----------------------------------------"
    if marker not in text:
        marker = "\t# -- Web application (SPA) -----------------------------------------------------"
    if marker not in text:
        raise SystemExit(f"Caddy route insertion marker not found in {path}")
    discovery_route = """\t# -- Discovery score webhook ---------------------------------------------------
\t# The scorer validates X-Webhook-Secret before updating the Paca task.
\t@discovery_score method POST path /hooks/discovery-score
\thandle @discovery_score {
\t\trewrite * /score
\t\treverse_proxy discovery-scorer:8091
\t}

"""
    text = text.replace(marker, discovery_route + marker, 1)
    path.write_text(text)
    print(f"added discovery scorer route to {path}")

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
