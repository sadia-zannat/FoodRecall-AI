# CURRENT STATUS — V0.8 LOCAL DEVELOPMENT CANDIDATE (24 Oct 2026)

Scout Intent implementation and independently authored local tests are available; NVIDIA/Zetaris live integration, upstream Meterless conformance, LangGraph runtime, FDA live sync and hosting are NOT verified. No real inventory. Read `V08_RELEASE_AUDIT_AND_HANDOFF.md`. Historical status below does not supersede this statement.

---

# FoodRecall AI V0.7 — Verified Local Engineering Handoff (23 October 2026)

**READ FIRST:** `V07_RELEASE_AUDIT_AND_HANDOFF.md` + `HUMAN_ONLY_NEXT_ACTIONS_BN.md`. The source-grounded AI response engine, evidence-aware conversation, simpler investigation interface, per-account local thread scope, and 75 regression tests are implemented. This is the complete **current local handoff ZIP**, NOT a live-sponsor-verified or production-ready Final V1.0. History below is retained for audit.

---

# FoodRecall AI v0.6 (2026-10-23) — VERIFIED LOCAL, NOT FINAL

**Read `V06_AUDIT_AND_HANDOFF.md` and `HUMAN_ONLY_NEXT_ACTIONS_BN.md` first.** This checkpoint adds conservative Zetaris exact-ID candidate reconciliation, remote private-API read protection, preflight and tests. Sponsor integrations and public deployment remain UNVERIFIED. All V0.5 content below is retained as historical reference.

---

# FoodRecall AI V0.5 — Offline Pre-Final Status (2026-10-20)

**VERIFIED LOCAL ONLY:** 53/53 Python tests, 65/65 independently declared synthetic decision-dependency cases, local Uvicorn HTTP smoke, bridge-backed Chromium UI interactions, 8-locale dictionary checks. Actual live sponsor integrations, LangGraph package and public deployment remain BLOCKED or NOT IMPLEMENTED. Existing V0.4 history is retained below.

**Key changes:** evidence-preserving Zetaris source projection with explicit no-match policy, narrower transport-error validation; tests for sponsor payload edge cases; realistic security headers; safer sponsor connectivity/test script; CI workflow created but not run on GitHub; documented synthetic evaluation and one-step user guide. User's accounts/credentials and real Cursor use are required for later progress. Pre-22 Oct work must be disclosed.

**Main continuation:** `NEXT_USER_ACTIONS_BN.md`, then `PRE_FINAL_AUDIT.md` and `BLOCKERS.md`. Do not deploy mutation endpoints publicly.

---

# FoodRecall AI V0.4 — Local Checkpoint Status (2026-10-14)

**VERIFIED:** Source code and fully runnable local training application built on V0.3. **Not** the final hackathon submission, not publicly deployed, and **not** production-secure for real companies. Pre-existing work before 22 Oct MUST be disclosed.

## Verified in this environment
- Independent V0.3 baseline: **34/34** tests passed before edits.
- V0.4 regression plus 10 new authentication, RBAC, CSRF, exact-identity approval, temporal decision revalidation, unrelated-evidence/critical-evidence distinctions and no-duplicate-hold tests: **44/44 pytest passed**.
- Real Uvicorn localhost TCP HTTP: sign-in, actual session cookie and CSRF, proposal → approve → material evidence update → stale rejection with diff → new approval → execute/verify → repeat idempotently → sign out. DB state persists to SQLite for the run.
- Real Chromium JS with FastAPI bridge: login, language/RTL/theme, agent runs, QA workflow, view Decision Diff, verified local hold, FDA archive, traceability, mobile view, sign out. NOT direct external browser or public host.
- Original localization validators 8×115 primary keys and 8×29 V0.2 strings remained intact. New V0.4 sign-in and decision copy provided in eight locales; source evidence remains unmodified.
- Session cookie token stored as SHA-256 in DB; password as salted PBKDF2; CSRF token/role checked server-side; `X-Demo-Role` ignored; local-only mutation restriction remains.
- Material change in supplier E-03 and lot RB-073 invalidates prior approval. A noncritical analyst note does not. Pre-V0.4 proposals fail closed. Decision Diff shows before and after states.
- Project includes `PROJECT_STATUS.md`, `CHANGELOG.md`, `NEXT_STEPS.md`, `TEST_REPORT.md`, `BLOCKERS.md`, screenshots and exact Windows launch instructions.

## PARTIALLY VERIFIED / NOT PRODUCTION READY
- This is a single-tenant LOCAL TRAINING identity system with QA/analyst/auditor. Not OAuth/MFA, hosted tenant isolation, production secrets manager, multi-worker concurrency safety, write-once audit store or security audit.
- Actual LangGraph StateGraph only import-path code tested/verified through fallback and mock, not runtime (cannot install package due unavailable network in this container).
- Actual NVIDIA Nemotron, Zetaris, Meterless integrations not exercised live. CUDA/GPU not needed for local training fallback.
- FDA public API retrieval did not succeed live in this environment; connector tests use mocked response with provenance and versioned local SQL.
- Browser runs via FastAPI bridge and separate local Uvicorn HTTP; not Chromium TCP navigation/public website. Public production deployment NOT DONE.
- Cursor development use was NOT performed here; ChatGPT Chat Mode wrote V0.4. Required sponsor proof must come from user's actual Cursor work.

## Command summary
- Windows: double-click `RUN_WINDOWS.bat`; on first boot terminal prints random local QA and analyst passwords ONCE. Visit `http://127.0.0.1:8000` and sign in.
- Password reset after initial start: `.\.venv\Scripts\python.exe scripts\manage_users.py`.
- Tests: `.\.venv\Scripts\python.exe -m pytest backend\tests -q`; local TCP `.\.venv\Scripts\python.exe scripts\test_http_v04.py`; Chromium `.\.venv\Scripts\python.exe scripts\browser_v04_smoke.py` after Playwright installed.

## Next
Follow `V04_CLICK_BY_CLICK_SETUP.md`: actual Cursor usage + Zetaris data onboarding + NVIDIA authorized Nemotron model and tool calls + LangGraph installed/executed + FDA live data + sponsor compliance/eligibility clarification; then production-grade final evaluation/deployment and independent audit.
