## V0.8 — 2026-10-24 (NEW, local development candidate)

- Added in-process Python Meterless Scout Intent specification adaptation, a relevant 8-intent registry, signing and verifying scoped 5-minute tool execution contracts.
- Enabled safe rejection of unsafe requests, tampered / expired / unauthorized contracts and out-of-scope provider tool suggestions; trace events stored.
- Hardened malformed model-tool response parsing. Added a guarded synthetic-only HTTPS demo opt-in mode and related security tests.
- Extended Windows + CI tests with 50-case local Scout evaluation, and supplied updated docs + presentation.
- **Live NVIDIA/Zetaris/FDA, actual LangGraph, upstream Meterless eval and production deployment remain unverified.**

---

# FoodRecall AI Changelog

## V0.4 (2026-10-14) — Verified local training auth and Decision Validity Engine
- STARTED from existing V0.3 50-file verified checkpoint; passed all 34 existing tests before edits.
- NEW: `backend/security.py` local account bootstrap and password reset, signed-in identity with PBKDF2 salted passwords, HttpOnly sessions, CSRF, RBAC, lockout, auth audit, session revocation.
- NEW: `backend/decision_v04.py` case-specific dependencies, critical evidence snapshot and material scope digest, stale blocking and structured decision diff, legacy proposal fail-closed.
- MODIFIED `backend/app.py` to require real server-side session + CSRF + role, preserve local-only restriction, ignore fake role header, add sign-in/user management and decision diff API; retain V0.2 FDA and V0.3 read-only agent tools.
- MODIFIED `frontend/app.js`, `styles.css` for authenticated login/logout, no fake selector, role control, before/after diff, eight-language sign-in text, mobile and theme regression.
- NEW: `backend/tests/test_v04.py` with 10 focused tests. Migrated old backend tests to authenticate through the real API; no production bypass.
- NEW: `scripts/browser_v04_smoke.py`, `scripts/test_http_v04.py`, `scripts/manage_users.py`; legacy browser/HTTP invocations forward to replacement authenticated test flows.
- NEW docs and four V0.4 screenshots.
- No actual API key created. No live NVIDIA/Zetaris/FDA integration or production deployment is asserted.

## V0.3 (prior checkpoint)
See `V03_ARCHITECTURE.md`, and existing source adapters/agent files. Read-only agent trace and local persistence with mock-tested model/tenant interfaces.

## V0.2 (prior checkpoint)
Versioned FDA archival adapter, synthetic EPCIS traceability, local demo workflows and localization.

## V0.5 — Offline Pre-Final Audit (20 Oct 2026)
- Zetaris tenant response parsing and per-source evidence/citations; no automatic FDA↔inventory association.
- 65 labeled synthetic temporal decision-regression scenarios with measured elapsed time and JSON results.
- HTTP security headers and regression tests for browser isolation, authentication cache policy, and remote-write prohibition.
- Model-selected tool-call live probe, Zetaris row-parser live probe, Windows QA script and CI definition (CI not run online).
- All pre-existing work preserved; sponsor live access/production release remain blocked.
