# V0.1 Baseline Audit (before modification)

**Original:** `FoodRecall_AI_V0.1_Runnable(4).zip` — retained separately and was not modified.

## Verified source structure
- FastAPI (`backend/app.py`), SQLite, independent static JavaScript frontend and CSS.
- 8-language dictionary, light/dark, responsive layout, seeded DEMO-001 case, lots RB-071/072/073/090.
- Deterministic investigation + evidence snapshots, local demo proposals, approval/stale-protection and idempotent SQLite hold execution + readback.
- Existing tests present: `backend/tests/test_api.py` (14 tests), JS dictionary check and Chromium smoke script.

## Independent baseline executions
- `python -m pytest backend/tests -q`: **14 passed**.
- `node scripts/test_i18n.mjs`: **8 locales × 115 keys passed**.
- `python scripts/browser_smoke.py`: **passed DOM / FastAPI TestClient bridge** for V0.1 workflow, mobile, languages and theme. NOT public browser networking.

## Material problems / risks
1. The four `tool_trace` steps are deterministic descriptors from one function — **not independently orchestrated LLM tools**. Mislabeling these as autonomous agent collaboration would be false.
2. `X-Demo-Role` is user-controlled and NOT real identity/permission verification.
3. `POST /api/demo/reset` and `/simulate-revision` were unrestricted; V0.2 blocks remote mutation endpoints but still lacks real auth.
4. The historical FDA feed was an optional direct API fetch, not persistent, provenance-verified or connected to investigator review.
5. Real model-generated text may lack independently verified citations; no NVIDIA live access confirmed.
6. No Zetaris, Meterless or proven Cursor development evidence.
7. No verified production hosting or independent commercial inventory integration.

## Preserve / extend
**Preserved:** baseline local safety flow and 8-locale shell. **Extended in V0.2:** FDA persistence/versioning, synthetic EPCIS-shaped event graph, read-only comparison, tests, local-only mutation protection. **Deferred:** LangGraph/Nemotron/Zetaris, evidence-bound credentialed authorization, external inventory, deployment.
