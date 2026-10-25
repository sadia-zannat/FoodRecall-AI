# FoodRecall AI v0.6 — Source-audited local checkpoint (23 October 2026)

**Release verdict: VERIFIED LOCAL CHECKPOINT; NOT FINAL V1.0; NOT PRODUCTION READY.**

This package was revised from the user-supplied original `FoodRecall_AI_V0.5_PreFinal_Offline_Audited(1).zip`. The entire 0.5 feature set (UI, login, QA approvals, selective evidence invalidation, FDA archive, EPCIS synthetic explorer and offline agent) is preserved. The 0.6 changes were developed AFTER the 22 October build start; earlier code already existed and must be disclosed if the rules require it.

## New changes actually implemented

1. `backend/source_reconciliation.py` analyzes two *actually returned* Zetaris query result sets using exact composite `(gtin, lot_id or lot_number)` equality, never product-name similarity. It distinguishes `UNVERIFIED_JOIN_CANDIDATE` from verified operational inventory links, returns ID conflicts, and bounds preview size. No stock modifications.
2. `backend/sponsor_evidence.py` integrates conservative reconciliation only when both provider result sets parse. If a tenant returns an unknown schema, the result stays `UNRESOLVED_SOURCE_SCHEMA`. No fake fallback rows or claimed FDA-to-inventory join.
3. `backend/agent_v03.py` makes the exact candidate and conflict counts available in observable grounded answers when Zetaris queries really execute. The model is not permitted to approve or execute holds.
4. `backend/app.py` now rejects **remote GETs to private API routes**, not only mutations. This closes V0.5's loophole where a remotely exposed local server could reveal case, audit and investigation data. `/api/health` and the explicitly public `/api/public/openfda` remain available. This does NOT provide production identity/tenant security.
5. `scripts/preflight.py` and `RUN_PREFLIGHT_WINDOWS.bat` produce secret-safe dependency readiness evidence and require explicit `--live` opt-in for outbound sponsor probes.
6. Agent evaluation now marks failed/unconfigured requested Zetaris evidence as **PARTIAL_SOURCES_UNAVAILABLE**, persists a partial run status and never disguises absent source results as completed.
7. Added independently runnable tests for positive/negative exact joins, conflicts, zero-padding, injection-like strings, bounded previews, provider failure, read boundary, and false live-readiness claims.

## Commands executed in this container

| Test | Observed result | Scope / caveat |
| --- | --- | --- |
| `python -m pytest backend/tests -q` | **67/67 PASS** | Offline functional/mocked/regression tests |
| `python scripts/evaluate_release.py` | **65/65 PASS** | Synthetic decision-dependency cases, *not* real recall detection precision |
| `python scripts/test_http_v04.py` | **PASS** | Actual loopback Uvicorn + HTTP, SQLite, authentication, CSRF and QA flow |
| `python scripts/browser_v04_smoke.py` | **PASS** | Chromium JS + TestClient bridge, not public-host navigation |
| `node scripts/test_i18n.mjs` | **PASS** | 8 locales × 115 keys |
| `node scripts/test_v02_locales.mjs` | **PASS** | 8 locales × 29 additional strings |
| `python scripts/preflight.py` | **COMPLETED** | Read-only local readiness; no live provider traffic |
| Live `check_live_integrations.py` probes | **BLOCKED** | NVIDIA key/model and Zetaris tenant/token/mapped tables absent |
| LangGraph runtime | **BLOCKED** | Cannot install `langgraph` here due DNS/index connectivity; native fallback tested |
| Real live openFDA sync | **NOT VERIFIED** | Outbound access unavailable in this execution environment |
| Direct public production browser/deployment | **NOT VERIFIED** | No authorized host or production security environment |

## The biggest product limitation

The current inventory and supplier lots are fictional training records. Merely fetching authentic FDA recalls and two Zetaris tables does NOT prove that a recalled product exists in company inventory. Without issuer-approved, authoritative recall-to-GTIN-to-lot master data and an operational readback, the final system MUST NOT classify operational lots as confirmed nor issue real holds. Exact joins are review candidates only. This package makes that distinction explicit; real deployments need an approved connector and tenant-specific policies.

## Vendor documentation used as integration reference

- Zetaris official getting started: https://github.com/zetaris/getting-started/blob/main/START-HERE.md
- Zetaris official local install: https://github.com/zetaris/getting-started/blob/main/docs/install/updated_zetaris_installation_guide.md
- Zetaris official SQL API: https://kbase.zetaris.com/knowledge/rest-api
- NVIDIA NIM tool calling: https://docs.nvidia.com/nim/large-language-models/1.15.0/function-calling.html
- openFDA limitations: https://open.fda.gov/apis/food/enforcement/

These references help with the user's external setup. No proprietary platform images or API tokens are bundled with this source ZIP.

## Integrity check order

On a **freshly extracted** ZIP, `BUILD_MANIFEST_SHA256.txt` hashes all distributed files. Verify the manifest **before** running tests; `scripts/browser_v04_smoke.py` intentionally regenerates screenshot PNGs and `scripts/evaluate_release.py` regenerates timestamped evaluation JSON. Therefore a *post-test* comparison to the pristine artifact's full manifest will differ even when tests succeed. This does not indicate source tampering. To repeat a pristine manifest check, extract a fresh copy of the original ZIP.
