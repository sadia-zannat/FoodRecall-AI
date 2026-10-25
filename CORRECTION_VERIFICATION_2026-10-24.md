# FoodRecall AI — combined-question corrective release

Date: 2026-10-24. Build category: **local corrected full project** (not production-ready V1.0).

## User-visible bug addressed

A multi-part question asking for **affected lots**, **uncertain lots**, and **supporting evidence** previously selected only the `uncertain` intent. `backend/answer_v07.py` now detects both requests before prioritizing narrow intents, and `make_answer` composes source-limited results for every requested group. It cites only evidence retrieved in that run and explicitly states that shipment mention alone is not an allergen-exposure confirmation. Saved historical answers are not retroactively rewritten; rerun the question after installing the corrected build.

Question: `Which lots are affected, which lots remain uncertain, and what evidence supports these classifications?`
Expected new synthetic-case response includes `RB-071 (120 units)`, `RB-072 (85 units)`, and `RB-073 (46 units)`, with retrieved E-01/E-02/E-03 evidence IDs and caveats.

## Actually executed locally (fresh extracted baseline, test environment)

- `python -m pytest -q backend/tests`: **89 passed** (4 direct multi-part regression tests).
- `python scripts/evaluate_scout.py`: **50/50 authored local test cases**; **not** official Meterless upstream conformance.
- `python scripts/evaluate_release.py`: **65/65 synthetic evidence-dependency scenarios**.
- `node scripts/test_i18n.mjs`: **PASS** (eight locale dictionaries).
- `node scripts/test_user_branding.mjs`: **PASS** (no visible internal V0.8 label).
- `python scripts/test_http_release.py`: **PASS** local TCP, CSRF, QA approvals, revision invalidation and SQLite readback.
- `python scripts/browser_combined_question_smoke.py`: **PASS** real headless Chromium JS plus authenticated FastAPI TestClient bridge; **not a deployed remote browser**.
- ZIP integrity, clean extraction, and SHA-256 content checks: performed during final packaging.

## Still outstanding, not misrepresented

Real NVIDIA Nemotron inference, Zetaris tenant SQL, official upstream Meterless runtime/evaluation, genuine LangGraph runtime, live FDA API sync, real inventory verification, deployed site, and HackOS submission have **not** been demonstrated in this release. Demo fixtures do not constitute real food-recall determinations. No secrets or live SQLite database are packaged.
