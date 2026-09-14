# Paca failure injection (intake resilience)

Verify that document intake surfaces Paca API failures loudly — non-empty component `error`, Witdem failed outcome, and a user-visible failure — instead of silently succeeding.

**Status: not yet executed.** This procedure is documented for Task 11; live injection on the VPS is deferred until intake → Paca wiring (Task 9) is deployed.

## Prerequisites

- Paca running on the Hostinger VPS (`/opt/ticket-workflow-system/paca`)
- Document intake deployed with Haystack → Paca wiring (`PACA_API_URL`, `PACA_API_KEY`, `PACA_PROJECT_ID`)
- Witdem instrumentation enabled on the intake pipeline

## Procedure

1. **Stop the Paca API container** on the VPS (leave other stack services as-is if possible, or stop the whole compose stack briefly):

   ```bash
   cd /opt/ticket-workflow-system/paca
   docker compose -f docker-compose.yml -f docker-compose.override.yml ps
   # Identify the API/gateway service name from the release compose, then:
   docker compose -f docker-compose.yml -f docker-compose.override.yml stop <api-or-gateway-service>
   ```

2. **Run one document intake** (staging or prod) with a test document — same path as a normal intake run.

3. **Expect failure signals:**
   - `CreatePacaTask` and/or `CreatePacaDocument` return a non-empty `error` field
   - Witdem run outcome is **failed** (not success)
   - User-visible confirmation or chat reflects the failure (no silent drop)

4. **Restart Paca:**

   ```bash
   cd /opt/ticket-workflow-system/paca
   docker compose \
     -f docker-compose.yml \
     -f docker-compose.override.yml \
     --env-file .env \
     up -d --scale ai-agent=0
   ```

5. **Run intake again** with the same or another test document; confirm Paca task + document are created and Witdem outcome is success.

## Record results

After the first live run, append a dated entry to `docs/verification-log.md` with:

- Date and environment (staging/prod)
- Which service was stopped
- Observed `error` payload (redact secrets)
- Witdem run link or ID
- Pass/fail for each expected signal above

## Related

- Deploy: [deploy-hostinger-paca.md](deploy-hostinger-paca.md)
- Intake field mapping: [intake-paca-mapping.md](intake-paca-mapping.md)
- CI deploy: `.github/workflows/deploy-paca.yml`
