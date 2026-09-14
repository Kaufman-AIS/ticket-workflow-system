# Intake → Paca field mapping

Maps document intake extract fields to Paca task and document fields. Used when wiring Haystack intake to `CreatePacaTask` and `CreatePacaDocument` (Task 9).

Google Tasks behaviour stays **unchanged** — Paca is additive and runs in parallel.

## Environment

| Variable | Purpose |
| --- | --- |
| `PACA_API_URL` | Paca API base URL (e.g. `https://paca.kaufman-ais.com`) |
| `PACA_API_KEY` | API key with project write access |
| `PACA_PROJECT_ID` | Target Paca project for intake-created tasks/docs |

## Field mapping

| Intake field | Paca target | Notes |
| --- | --- | --- |
| Document type + issuer | Task **title** | Prefix pattern: `[invoice] ACME`, `[contract] Vendor Name`, etc. |
| Extracted summary | Task **description** | Short human-readable summary from the extract step |
| Full extract JSON / markdown | Document **body** | Attach via `CreatePacaDocument` (`markdown` field) |
| Drive file link (if any) | Task **description** | Append link to description after summary |
| Google Tasks | *(unchanged)* | Existing intake path; do not remove or gate on Paca |

## Wiring order

After a successful extract step in the intake pipeline:

1. `CreatePacaTask` — title and description from the mapping above
2. `CreatePacaDocument` — title (e.g. same as task or document filename) and markdown body from full extract

If either component returns a non-empty `error`, treat the pipeline outcome as **failed** (Witdem + user-visible failure). See [failure-injection.md](failure-injection.md).

## Reference implementation

- Components: `integrations/haystack_paca/components.py`
- Wiring sketch: `integrations/haystack_paca/pipeline_snippet.py`
- Cross-repo intake PR: `onyx-witdem-document-intake` (separate repository)
