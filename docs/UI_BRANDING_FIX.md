# FoodRecall AI — User-facing branding correction (24 Oct 2026)

The project version "V0.8" is an **internal engineering checkpoint**. It is not a public product version and should not appear in user-facing screens.

## Scoped correction
- Login brand now reads "FoodRecall AI" legibly on the white card.
- Login subtitle: "Evidence-based recall investigation" (no build identifier).
- Dashboard footer retains the required training-mode disclaimer but no internal version.
- Agent Investigation overline reads "FOODRECALL AI" (no build identifier).
- Existing read-only, training-only, and non-live-provider warnings are preserved.
- No changes were made to authorization, databases, provider keys, or remote deployment behavior.

## Verification performed here
- `python -m pytest backend/tests -q` — 85 passed.
- `python scripts/browser_v04_smoke.py` — Chromium browser UI/auth/CSRF workflow passed, including new login contrast/title assertions.
- `python scripts/test_http_v04.py` — real localhost HTTP workflow passed.
- `python scripts/evaluate_scout.py` — 50/50 authored local cases passed (NOT official Meterless upstream evaluation).
- `python scripts/evaluate_release.py` — local synthetic evidence evaluation passed.
- `node scripts/test_user_branding.mjs` — passed.
- `node scripts/test_i18n.mjs` and `node scripts/test_v02_locales.mjs` — passed.

**Status: branding correction only.** Live NVIDIA/Zetaris/Meterless upstream integration acceptance, hosted deployment, and production authorization remain pending as described in the V0.8 audit report.
