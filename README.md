# FoodRecall AI V0.8 — Local development candidate (24 October 2026)

**CURRENT RELEASE FILES:** `V08_RELEASE_AUDIT_AND_HANDOFF.md`, `V08_HUMAN_ACTIONS_BN.md`, `docs/SAFE_HOSTED_TRAINING_DEMO.md`.

**DO NOT CALL THIS FINAL V1.0 OR LIVE-SPONSOR VERIFIED.** V0.8 implements a domain-scoped
Python adaptation of the open-source Meterless **Scout Intent** engine specification:
Sense / Interpret / Guard / Route / Recommend with five-minute signed contracts
verified before every read-only investigation tool call. Local engine evaluations and
regression tests run; upstream Meterless `npm run evals` and real NVIDIA/Zetaris/FDA
connections remain unverified here. Genuine LangGraph runtime is optional and was
not importable in this build environment. All inventory records are fictional.

**Quick start:** Extract the ZIP, double-click `RUN_WINDOWS.bat`, sign in with the
QA password printed on first launch, then run `RUN_ALL_TESTS_WINDOWS.bat`.
Never paste API keys into chat or upload them to GitHub. Optional demo hosting
requires explicit `FOODRECALL_DEMO_REMOTE=1` and `FOODRECALL_PUBLIC_ORIGIN` with
HTTPS plus strong private passwords, and is for synthetic data only.

**Evidence:** `evaluation/results_scout_v08.json`; test logs in `verification/`.

---

# FoodRecall AI V0.7 — Verified Local Engineering Handoff (23 October 2026)

**READ FIRST:** `V07_RELEASE_AUDIT_AND_HANDOFF.md` + `HUMAN_ONLY_NEXT_ACTIONS_BN.md`. The source-grounded AI response engine, evidence-aware conversation, simpler investigation interface, per-account local thread scope, and 75 regression tests are implemented. This is the complete **current local handoff ZIP**, NOT a live-sponsor-verified or production-ready Final V1.0. History below is retained for audit.

---

# FoodRecall AI v0.6 — Verified Local Integration-Ready Checkpoint

**Read `V06_AUDIT_AND_HANDOFF.md` and `HUMAN_ONLY_NEXT_ACTIONS_BN.md` first.** This checkpoint adds conservative Zetaris exact-ID candidate reconciliation, remote private-API read protection, preflight and tests. Sponsor integrations and public deployment remain UNVERIFIED. All V0.5 content below is retained as historical reference.

---

# FoodRecall AI V0.5 — Offline Pre-Final QA Checkpoint

**Status: VERIFIED local workflow and additional synthetic evaluation; NOT production-ready or sponsor-compliant yet.** FoodRecall AI is an evidence-grounded food recall investigation and local simulated inventory-containment workbench. **No real warehouse operations.** This version **replaces the V0.3 forgeable demo-role switch** with local password authentication, server-side QA/analyst/auditor RBAC, short-lived HttpOnly sessions, CSRF protection, and an independently testable selective Decision Validity Engine. It is not a certified food-safety service or enterprise multi-tenant IAM.

## First launch on Windows (click-by-click)

1. Extract the ZIP. Open the **`foodrecall-ai` folder** containing `RUN_WINDOWS.bat`.
2. Double-click **`RUN_WINDOWS.bat`** (Python 3.10+ required). A terminal opens, creates `.venv`, installs packages and starts Uvicorn bound to **127.0.0.1:8000**.
3. On the **first start only**, find `LOCAL TRAINING LOGIN` in that terminal. It displays two generated usernames/passwords for **QA manager** and **analyst**. Save them privately; never photograph or publish these credentials. If you had configured `FOODRECALL_BOOTSTRAP_PASSWORD` / `FOODRECALL_ANALYST_PASSWORD`, use those instead.
4. Open **http://127.0.0.1:8000/**. You will see a real sign-in screen. Sign in with **qa@local.foodrecall** and the first-start password. Click **Sign in securely**.
5. Choose **Investigation** to inspect fictional evidence; **Approvals & actions** to create a proposal, approve it as QA, **Simulate evidence update**, open **Decision Diff**, then create/reapprove and execute a new *synthetic training* hold. Sign out to revoke your session.
6. If password is lost, open a PowerShell terminal in the project folder and run `.\.venv\Scripts\python.exe scripts\manage_users.py` to reset one account (interactive hidden input).

**No key is needed** to use offline mode. **Do not expose localhost writes to the public internet.** The frontend authenticates with an HttpOnly SameSite cookie and holds its CSRF token in JS memory; it refreshes the CSRF token from `/api/auth/me` after a page reload. Client-side role changes and X-Demo-Role headers have NO authorization effect.

### Exact PowerShell commands (from project root)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Test from another terminal:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q
.\.venv\Scripts\python.exe scripts\test_http_v04.py
node scripts\test_i18n.mjs
node scripts\test_v02_locales.mjs
# If Playwright/browser installed separately:
.\.venv\Scripts\python.exe -m pip install playwright
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe scripts\browser_v04_smoke.py
```

**Old test commands** (`browser_smoke.py`, `browser_v03_smoke.py`, `test_http_release.py`, `test_http_v02.py`, `test_http_v03.py`) now run the updated V0.4 authenticated test workflow. They no longer assume a forgeable demo-role header.

## V0.4 additions

- `backend/security.py`: PBKDF2-HMAC-SHA256 password hashing with random salt, generic login failures, 5-failure/10-minute lockout, session expiry, hashed session tokens, HttpOnly SameSite cookies, CSRF, auditable logins, server-side role decisions, three local training roles.
- `backend/decision_v04.py`: proposal-specific critical dependency hashes; scope of confirmed/uncertain lots and critical supporting source versions; unrelated `analyst_note` updates **do not stale approvals**. Material supplier/product/lot changes do. Shows old-versus-new Decision Diff; unknown migrated proposals fail closed.
- New auth API: `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout`, `POST /api/auth/users` (QA-only local training setup). Every POST/PUT/PATCH/DELETE API request other than login requires a valid local session + CSRF + permitted role; public remote writes are blocked separately.
- `GET /api/proposals/{id}/decision-diff`, actual backend state updates, on-screen diff and authenticated identity; client-supplied reviewer display name cannot impersonate the actual actor.
- Sign-in and role messaging localized for eight UI languages, persistent light/dark and mobile styles; prior V0.3 agent tools and FDA/EPCIS read-only data views maintained.

**Privacy & deployment limits:** this is a *single-organization training* scheme, not independently audited production IAM. No row-level isolation between real organizations, secure hosting plan, OAuth/MFA, protected production audit ledger, rate-limiting proxy, production database migration, or connection to ERP. Do not deploy public inventory mutation endpoints. The code is a local verified checkpoint, not regulatory compliance evidence.

## External sponsor status

- **NVIDIA Nemotron**: compatible adapter with MOCKED tests only; live token/model/tool-call inference BLOCKED. A configured key does not prove model entitlement.
- **Zetaris**: validated tenant SQL connector and MOCKED tests only; authentic tenant/idToken/table mapping/query BLOCKED.
- **Meterless**: configurable gateway path, no live validation.
- **LangGraph**: optional code path exists from V0.3, but dependency install and active execution NOT VERIFIED here. Native offline orchestration is explicitly labeled and **not LangGraph**.
- **FDA**: mocked connector tests, data archive and provenance verified locally. Real FDA API sync BLOCKED in this environment; 0 fabricated published recall records.
- **Cursor**: this checkpoint was developed with ChatGPT Chat Mode, **not Cursor**. Actual Cursor use with evidence is necessary before claiming sponsor compliance.
- **Public deployment**: NOT IMPLEMENTED. Important: **pre-22 October development must be declared** for Open Agent Hackathon 2026.

Read `V04_CLICK_BY_CLICK_SETUP.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, `TEST_REPORT.md`, `NEXT_STEPS.md`, `BLOCKERS.md`, `SPONSOR_INTEGRATION_REPORT.md` for continuation.

## V0.5 offline QA handoff (20 October 2026)

The v0.4 verified local workbench has been improved with tenant-response-aware **Zetaris row projection** (mocked protocol tests, not live), stronger browser headers and 65 user-independent, synthetic **evidence-dependency** regression scenarios. Current source code may still show v0.4-era component labels from the original UI; the API version is `0.5.0-offline-audit`. This is an honest **pre-final** checkpoint, not a full hackathon release.

Run from Windows project root (after `RUN_WINDOWS.bat` has created `.venv`):

```powershell
.\RUN_ALL_TESTS_WINDOWS.bat
# Optional: run scripts separately
.\.venv\Scripts\python.exe -m pytest backend\tests -q
.\.venv\Scripts\python.exe scripts\evaluate_release.py
.\.venv\Scripts\python.exe scripts\test_http_v04.py
```

With authorized sponsor keys configured **privately**, opt-in live verification:

```powershell
.\.venv\Scripts\python.exe scripts\check_live_integrations.py --nvidia --nvidia-tools
.\.venv\Scripts\python.exe scripts\check_live_integrations.py --zetaris
```

These commands must complete successfully on **your environment**, using an entitled Nemotron model and a real Zetaris tenant, before those integrations can be labeled live verified. The `--nvidia-tools` model must return a real `case_notice` tool call. Read `PRE_FINAL_AUDIT.md` and `NEXT_USER_ACTIONS_BN.md` first.

**Synthetic evaluation methodology:** 13 manually specified material/nonmaterial dependency-change categories × 5 variants = 65 local isolated SQLite scenarios. No FDA records, real shipment links, external inference or cloud API access participate. The benchmark is not an unbiased external dataset and doesn't establish full clinical/food safety or enterprise readiness.
