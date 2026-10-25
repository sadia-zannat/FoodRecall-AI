# V0.5 — Actual Local Verification (2026-10-20)

Proof type and limitations MUST remain separate. New source code and future sponsor accounts do not establish live integration. **Synthetic evaluation 65/65 is an internal regression score, NOT food-lot matching precision, recall, F1 or externally validated performance.**

- Python tests: 53 passed (`python -m pytest backend/tests -q`). 44 original V0.4 + 6 sponsor-result projection tests + 3 defensive HTTP header/remote-write tests.
- Synthetic decision-dependency cases: 65/65 (`python scripts/evaluate_release.py`), manually declared 13 categories × 5 variants. Inspect `evaluation/results_evidence_dependencies.json` for p50/p95; isolated local SQLite, no external APIs.
- Actual Uvicorn localhost HTTP: PASS `python scripts/test_http_v04.py` (cookie, CSRF, QA approval, material evidence revision, stale block, idempotent local hold, state readback, logout).
- Browser: PASS `python scripts/browser_v04_smoke.py` (Chromium JS with FastAPI in-process bridge). **Direct Chromium→localhost failed** with ERR_BLOCKED_BY_ADMINISTRATOR; NOT public browser deployment testing.
- Localization: 8×115 primary keys and 8×29 V0.2 keys PASS (`node scripts/test_i18n.mjs`, `node scripts/test_v02_locales.mjs`).
- Live NVIDIA: BLOCKED (no credentials or authorized model). `--nvidia-tools` newly implemented but NOT exercised with live model.
- Live Zetaris: BLOCKED (no tenant, SQL endpoint/token). Projection test uses MOCKED API responses.
- LangGraph installed/executed: BLOCKED; pip package index unavailable. Native fallback explicitly labeled.
- FDA live: BLOCKED; no public FDA records verified from this environment.
- Meterless: BLOCKED; not configured or verified; requirement ambiguous in supplied docs.
- Cursor development: NOT PERFORMED in this assistant session; user must build/test real changes there.
- Docker image: NOT TESTED (Docker CLI unavailable). GitHub Actions workflow: CREATED, not executed on GitHub.
- Production deployment / IAM: NOT IMPLEMENTED. All code remains LOCAL TRAINING ONLY.

---

# V0.4 — Actual Test Report (2026-10-14)

| Type | Test(s) | Observed result | Evidence boundary |
|---|---|---|---|
| Baseline V0.3 | `python -m pytest backend/tests -q` before edits | **34 passed** | Real in-process DB/API, mocked sponsor transports |
| New V0.4 + regressions | `python -m pytest backend/tests -q` | **44 passed** | Real password/auth session/CSRF/SQLite local only |
| Actual localhost TCP HTTP | `python scripts/test_http_v04.py` | **PASS** | Real Uvicorn socket, anonymous 401, authenticated 200, CSRF 403, stale 409, SQLite readback, logout |
| Browser UI | `python scripts/browser_v04_smoke.py` | **PASS** | Real Chromium JS and click flows via in-process FastAPI bridge, **not** public browser/TCP navigation |
| i18n primary | `node scripts/test_i18n.mjs` | **PASS** | 8-language dictionary validation (legacy V0.1) |
| i18n new data pages | `node scripts/test_v02_locales.mjs` | **PASS** | V0.2 8-language supplementary dictionary |
| V0.4 auth/locales | Browser changed English→Bangla→Arabic RTL→English, login and logout | **PASS** | Form/role/diff strings in 8 dictionaries, limited end-to-end sampled languages |
| FDA external | Connect to api.fda.gov | **BLOCKED** | Tests only mocked; no real official records claimed |
| NVIDIA, Zetaris, Meterless | External authenticated access | **BLOCKED** | Provider adapters code/mocked tests, no live tokens/tenant |
| LangGraph execution | `StateGraph` runtime | **BLOCKED** | Not installed due network restrictions; actual orchestrator uses labeled native fallback |
| Real public deployment | HTTPS hosted browser E2E | **NOT IMPLEMENTED** | localhost training only |

## Key tests added
- Anonymous and forged X-Demo-Role denial; real session login/logout.
- Missing/invalid CSRF 403; analyst cannot impersonate QA; reviewer identity taken from server.
- QA audit-only account creation and read-only auditor.
- Unrelated analyst note does **not** invalidate; relevant evidence version and lot scope updates **do**; Decision Diff before/after.
- Unknown pre-V0.4 proposal fails closed; duplicate hold execution replays existing receipt.
- Remote client cannot mutate even with copied cookie/token.

## Limits
Local role security is *not* a substitute for true multi-tenant production IAM. No secret/value from real users was included in this package. Sample tests exercise synthetic data only.
