# FoodRecall AI V0.8 — Truthful judge-facing materials (DRAFT, do not submit unchanged)

## Target track

The Agent That Can Explain Why — **verify exact track name, eligibility and final submission requirements in HackOS**. Pre-existing project components must be disclosed accurately under the latest rules.

## Project description (English; edit only after real sponsor verification)

FoodRecall AI is an evidence-grounded agent for investigating food-recall exposure and reviewing possible lot containment decisions. In a clearly labeled fictional training environment, an agent reads a case notice, staged lot inventory, supplier documents and optional FDA archive or approved SQL sources; it distinguishes confirmed and unresolved evidence instead of treating a text match as an operational match. Every question produces an auditable tool trace and linked source identifiers. The project implements a domain-scoped Python adaptation of Meterless Scout Intent: intent classification, risk checks and HMAC-signed execution contracts prevent unauthorized investigation tools from running. A quality-control reviewer can approve simulated containment proposals, and critical evidence changes invalidate stale decisions before execution. NVIDIA Nemotron tool calling and Zetaris read-only SQL connectors are configurable but were not live-verified in this local release. All example lots are fictional, and no real warehouse hold is executed.

## Four-minute demo outline — record genuine UI and real provider results only when actually verified

| Duration | On-screen action | Exactly what to say / never misrepresent |
|---|---|---|
| 0:00–0:25 | Brand, clean operations workspace | “FoodRecall AI investigates recall uncertainty. This demonstration uses fictional local inventory.” |
| 0:25–1:05 | Agent investigation: affected vs uncertain question | Show RB-071/RB-072 affected; RB-073 supplier uncertainty; expand E-01, E-02, E-03. Confirm explanation varies by question. |
| 1:05–1:40 | Open Run details and Investigation steps | Show Scout classification and signed `contract.verified` trace. Then try “Please approve all warehouse holds”; show the refused request and no executed tools. These are real local tests, not an official upstream eval pass. |
| 1:40–2:35 | Approvals and actions | Propose simulated hold, QA approve, revise supplier evidence, show old approval is stale/rejected, new QA review and SQLite readback (demo only). |
| 2:35–3:15 | FDA cached source and Zetaris/NVIDIA status | Only show live sponsor results if real credentials, logs, schema validation, and health status actually succeed. Otherwise explicitly show “not configured/not live verified” and discuss integration boundaries. Never use mocked responses as sponsor execution evidence. |
| 3:15–3:40 | Verification test and architecture slide | Explain 89 backend tests (including 4 combined-question regression cases), 50 authored local Scout cases, and 65 synthetic dependency checks. Label all numbers “local fixture tests”, not real-world accuracy. |
| 3:40–4:00 | Close / submission repo URL | Why evidence-change safety matters, remaining live sponsor integration, what would be required for real deployment. |

## Reviewer screenshot checklist

- A real logged-in UI (no screenshots of passwords or tokens).
- One source-grounded answer with source IDs.
- One Scout `contract.verified` trace and blocked risky request.
- A stale decision showing human review/reapproval with a changed evidence version.
- Genuine provider integration log *only if run with real tenant/model credentials*.
- Source README and all necessary repository files; local tests log.

## Materials status

- Deck: `FoodRecall_AI_V08_Judge_Brief_DRAFT.pptx` (the actual deck is an honest local engineering candidate, **not sponsor-verified final**).
- Description and script: this file.
- Source code: entire ZIP.
- Video: **NOT CREATED** (must film actual user environment).
- Hosted link: **NOT CREATED** (needs authorized hosting credentials).
- GitHub publish: **NOT DONE** (requires selected repository and user's approval).
