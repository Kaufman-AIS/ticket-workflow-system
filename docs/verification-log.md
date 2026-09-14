# Verification log

## 2026-09-14 — Paca Hostinger TLS

- DNS: `paca.kaufman-ais.com` → `187.124.175.57` (confirmed via 8.8.8.8 / 1.1.1.1)
- Lean stack healthy on VPS (`agent-runner` scaled to 0; gateway `127.0.0.1:8090`)
- Certbot: certificate issued, HTTPS enabled
- `scripts/smoke_paca_health.sh https://paca.kaufman-ais.com` → OK
- `scripts/smoke_paca_api.py` against `https://paca.kaufman-ais.com` → OK (task + doc created)

Admin login: `https://paca.kaufman-ais.com/` (credentials in VPS `/opt/ticket-workflow-system/paca/.env`).
