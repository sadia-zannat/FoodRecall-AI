# V0.8 CURRENT SPONSOR STATUS (24 Oct 2026)

Meterless Scout Intent: in-process Python spec adaptation integrated with real signed tool-execution boundary and local tests; **not official upstream eval passed**. NVIDIA: optional tool calling only mock-tested. Zetaris: prepared read-only SQL adapter only fake-transport tested, no real tenant. Sponsor compliance not confirmed. Historical integration notes below.

---

# V0.5 Sponsor Verification Status (2026-10-20)

- **Zetaris:** `backend/zetaris.py` authenticated SQL adapter + `backend/sponsor_evidence.py` evidence projection; **MOCK TRANSPORT VERIFIED**, LIVE TENANT **BLOCKED**. Agent now retains bounded, parsed per-source row counts and citations, not fake cross-source matching; verification of impact on realistic decisions still pending.
- **NVIDIA Nemotron:** OpenAI-compatible tool-selection adapter + `scripts/check_live_integrations.py --nvidia-tools`, **MOCK TRANSPORT VERIFIED, LIVE BLOCKED**. True model-selected tool call required for certification.
- **Meterless:** endpoint configurable, no live access; requirement ambiguity awaiting organizer clarification.
- **Cursor:** code in this ZIP written in ChatGPT, NOT in Cursor. Genuine Cursor work with git commits or logs needed.
- **FDA:** API connector and cache protocol mocked-tested; external live record ingestion still blocked.

---

# V0.4 Sponsor Integration Report

| Tech | Current code | Actual live evidence | Remaining actions |
|---|---|---|---|
| NVIDIA Nemotron | OpenAI-compatible HTTPS tool-call adapter in `backend/agent_v03.py` | BLOCKED: no credential/model external access | Model page, key, test `--nvidia`, demonstrate `model_tool_calls` actual run |
| Zetaris | `backend/zetaris.py` REST SQL adapter, table allowlist, 12s timeout | BLOCKED: no instance/token/registered data access | Register two real/staged sources, run OpenSqlQuery in Postman and app |
| Meterless | Optional OpenAI-compatible gateway environment variables | BLOCKED: no access | Clarify official mandatory status; if required test actual model route |
| Cursor | No automatic IDE usage via ChatGPT | NOT VERIFIED | User must open repo in Cursor, implement/review meaningful change, record truthful proof |
| Bright Data | Optional only, not integrated | NOT IMPLEMENTED | Only if sponsor bounty / clear legal data advantage |

Do not infer sponsor points from filenames, comments, mock tests, documentation or account registration alone. `scripts/check_live_integrations.py` explicitly checks tokens only when user runs it in their approved local environment. A successful text completion isn't evidence of tool calling.
