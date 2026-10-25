# FoodRecall AI V0.7 — Local verified engineering handoff

**Created:** 23 October 2026 (UTC+6)

**Status: source + local UI + offline agent verified; external integration and production release NOT VERIFIED.** The project is not a commercial food-safety system and may not be deployed as-is to public users. This handoff builds on the user's original V0.6 archive; earlier V0.5/V0.6 reports are retained as history.

## What was really implemented in V0.7

- Question-sensitive source-grounded agent answers for affected, uncertain, sources, FDA archive, Zetaris, shipment evidence, safe next steps, and decision revisions. The agent no longer gives the same canned answer for every question.
- Bangla and English local deterministic answers for core investigation questions. Eight interface dictionaries remain available; other locales' offline answers fall back to English rather than claiming translation support that was not implemented. LLM response locale is requested when provider access exists.
- Second bounded, optional NVIDIA/Meterless chat completion for **supplemental** natural explanation after real tool execution. Structured response is subjected to allowlisted citation IDs, allowed lot IDs, numeric and unsafe-action guards. Failure falls back to a source-derived summary; a passing syntactic guard is **not factual certification**. Original verified counts cannot be overwritten by model prose.
- UI shows human-readable answers, evidence items, honest mode/status labels; hides raw trace/debug detail behind expandable controls; reduces decorative hero area.
- Per-account namespaced conversation threads, per-tab frontend identifiers and logout clearing transient conversation. Existing run logging remains; no cross-customer production isolation claim.
- Changed supplier evidence updates the explanation: RB-073 moves from uncertain to affected in the existing **training** revision; version 2 is reflected in a later investigation. Existing decision revalidation/QA approval behavior preserved.
- 8 additional local regression tests validating intent routing, BN, mocked explanatory response, fabricated citation/lot rejection, run scoping, and changed evidence.

## Actual execution evidence

| Check | Outcome | Important qualification |
|---|---|---|
| Python backend pytest | 75/75 PASS | Includes simulated/mock provider tests; not a live API call |
| Synthetic evidence-dependency evaluation | 65/65 PASS | Only tests internal temporal-dependency scenarios |
| TCP localhost Uvicorn + auth/CSRF QA workflow | PASS | Loopback SQLite training case, not production |
| Chromium browser smoke / UI | PASS | Real Chromium JS + TestClient bridge (not deployed browser) |
| Locale structure tests | PASS | 8×115 + 8×29 keys; not a linguistic quality review |
| Preflight (no outbound traffic) | Ran | No configured NVIDIA/Zetaris; LangGraph package unavailable |
| V0.7 ZIP manifest / clean extract | PASS | Verified before running mutating screenshot/evaluation tests |

## Known limits and blockers

1. **No NVIDIA live inference**: NVIDIA_API_KEY and compatible entitled NVIDIA_MODEL were not supplied. Test mocks prove code contracts only.
2. **No Zetaris live SQL**: real tenant instance/token/SQL endpoint and approved real source tables were not supplied. The Zetaris cross-source candidate logic remains unverified against a live schema.
3. **No verified FDA live sync**: Internet calls from this work environment were not used to ingest real FDA records. The FDA Enforcement API is historical/weekly, not a complete public alert feed.
4. **No physical inventory**: training lot RB-071/RB-072/RB-073/RB-090 and EPCIS events are fictional. No real company stock, supplier or regulatory linkage is verified. Even an exact GTIN+lot candidate does not authorize a hold.
5. **No production authorization / public deployment**: app is loopback-only local training. Session+CSRF/RBAC is not enterprise IAM, and staging holds only affect local SQLite. Do NOT bind it to 0.0.0.0 or put it behind a public reverse proxy.
6. **LangGraph optional package**: native orchestration fallback is tested. Genuine LangGraph execution requires installation and rerun on a network-enabled machine.
7. **Event proof**: Cursor usage, current rules eligibility for pre-existing work, external sponsor verification, GitHub, demo recording and submission require the user's authenticated tools/approval.

## Do not misrepresent

- Do not say "ChatGPT-equivalent", "autonomous production recalls", "100% accurate", "FDA verified warehouse match", "Zetaris connected", or "Nemotron live" based on offline tests.
- The model may compose an optional explanation; only pre-validated deterministic fields should drive any user decision, and food safety decisions require a qualified human reviewer.
- Tests executed here on 23 Oct are newly generated evidence. Historical screenshots/reports inside this package document prior releases; do not reinterpret them as fresh provider validation.

## Run locally

1. Extract the ZIP into a clean directory. In Windows double-click `RUN_WINDOWS.bat` and open `http://127.0.0.1:8000`.
2. Log in with the locally bootstrapped QA Manager credentials **shown in the terminal on first run**. Never upload a password or `.env` to GitHub.
3. Run `RUN_ALL_TESTS_WINDOWS.bat` from the project folder after base dependencies finish installing. To test exact sponsor connections, first configure credentials privately and run `RUN_PREFLIGHT_WINDOWS.bat`. External integration probes require an explicit opt-in.
4. Test at least: affected lots, why uncertain, what changed, QA approval with later supplier revision, and the source evidence panel.

## Source architecture

- `backend/agent_v03.py`: bounded planning/tools/orchestration, trace persistence, read-only operational boundary.
- `backend/answer_v07.py`: new source-grounded response, locale, optional model explanation + guarded fallback.
- `backend/source_reconciliation.py`: exact candidate logic, never authoritative physical lot join.
- `frontend/app.js`, `frontend/styles.css`: honest compact operational UI.
- `backend/tests/test_v07_conversation.py`: new adversarial and source-change regression tests.
- `verification/`: testing and readiness records (no secret tokens).

## FDA data warning

FDA states its Food Enforcement Report API is updated weekly and must not be used to issue public alerts or track recall lifecycle. See https://open.fda.gov/apis/food/enforcement/ .
