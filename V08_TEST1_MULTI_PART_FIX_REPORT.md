# FoodRecall AI — Test 1 combined-question correction

**Date:** 24 October 2026 (Asia/Dhaka)  
**Scope:** Backend question understanding and evidence-linked local answers only. Existing branding/UI unchanged.  
**Status:** Locally verified development patch; not sponsor-complete or production-ready.

## User-reported defect

Question: `Which lots are affected, which lots remain uncertain, and what evidence supports these classifications?`

Earlier response only described uncertainty of RB-073, omitting the two affected lots. Root cause was first-match priority in `backend/answer_v07.py`: `uncertain` overrode the other requested intents.

## Correction

- The offline answer router now recognizes combined **affected + uncertain** and **affected + evidence** questions, including a Bangla version.
- The answer lists **both** classifications, plus counts from the actual retrieved training inventory.
- Lot-specific citations are displayed only when the retrieved source text mentions that exact lot. A manifest is **not** treated as proof of a live safety incident.
- Missing inventory or evidence is stated as a limitation rather than inventing citations.
- Revision of supplier evidence updates the grouped result; previously completed classifications are never hardcoded.
- No warehouse, QA approval, or write action is executed by the agent.

## Verification executed in the isolated development copy

- `python -m pytest -q backend/tests` — **89/89 PASS** (85 prior + 4 new tests).
- `python scripts/evaluate_scout.py` — **50 authored local cases PASS** (not official Meterless evals).
- `python scripts/evaluate_release.py` — **65/65 synthetic evidence-dependency checks PASS**.
- `python scripts/test_http_release.py` — **PASS**, real localhost TCP/API authentication, CSRF, approval, stale protection, readback and logout.
- `python scripts/browser_combined_question_smoke.py` — **PASS**, real Chromium JS and authenticated TestClient bridge for the exact combined question; not public hosting.
- `node scripts/test_i18n.mjs` — **PASS**, existing UI dictionary validation.
- `node scripts/test_v02_locales.mjs` — **PASS**.
- `node scripts/test_user_branding.mjs` — **PASS**.

## Still not verified

- Genuine NVIDIA Nemotron live inference; Zetaris live tenant SQL; official upstream Meterless harness; genuine LangGraph environment execution; production security/deployment and real inventory joins.
- Original snapshot uses **fictional local training lots**, not actual FDA or company inventory.
- Other natural-language multi-part question formulations are not guaranteed without their own regression cases.

## Apply to your CURRENT Windows project

Prefer the small patch ZIP. Stop the old running server with `Ctrl+C` in its VS Code terminal, replace `backend/answer_v07.py`, optionally add new test/script, then start `RUN_WINDOWS.bat`. You **do not need** to replace or delete a SQLite database, reset passwords, extract a new full project, or alter UI files. Refresh browser and repeat the exact question; the old saved run will remain unchanged and a **new** answer will be correct.
