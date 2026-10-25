# FoodRecall AI V0.8 — Verified local development, NOT final V1.0

**Engineering date:** 24 October 2026 (Dhaka). **Baseline:** the exact user-supplied V0.7 handoff ZIP, clean extracted into a new work directory. The original ZIP was not edited.

## What V0.8 actually implements

1. **Meterless Scout Intent (domain-scoped Python implementation)**: `backend/scout_intent.py` follows the open-source five-stage Sense → Interpret → Guard → Route → Recommend spec. It uses a versioned, example-backed eight-intent registry for relevant food-recall investigation tasks; read-only capability routing; injection, role, scope, and operational-action guards; five-minute HMAC SHA-256 execution contracts. `backend/agent_v03.py` now refuses to execute investigation tools unless Scout's contract is current, untampered and explicitly authorizes the tool; evaluator retries receive **new linked** contracts. Structured traces include `scout.decision`, `contract.issued`, `contract.verified`, and refusal, without printing contract signatures, credentials or hidden model reasoning.
2. **Provider boundary**: Nemo-compatible LLM tool suggestions remain optional and are restricted to Scout's capability graph. Malformed tool responses cannot authorize tools or crash the agent's tool parser. Offline planning remains available and is honestly labeled; simulated provider responses never count as live verification.
3. **Conservative scope**: The local agent cannot issue, approve or execute real warehouse actions; existing QA manager permission, source-change revalidation, stale-decision blocking and readback remain intact. Source provenance and synthetic/real boundary preserved. Account role passed from authenticated request to Scout guards.
4. **Optional HTTPS-hosted *fictional demo***: explicit `FOODRECALL_DEMO_REMOTE=1`, exact HTTPS `FOODRECALL_PUBLIC_ORIGIN`, and two strong private initial passwords are required; anonymous GET access to private APIs and cross-site mutation origins are refused. Secure cookie + HSTS when enabled. This is **single-tenant synthetic demo only**; not an authorization to serve company, regulatory, or production data. Existing local loopback mode is the default.
5. **CI / human scripts**: local Scout test module and independent 50-case scenario/guard evaluation have been added to the Windows runner and GitHub Actions; source version displays V0.8, and brief Scout tool evidence is available inside the existing collapsed Run details, without UI clutter.

## Local executed verification

See `verification/V08_EXECUTION_EVIDENCE.txt`, `verification/PREFLIGHT_V08_LOCAL.json`, and `evaluation/results_scout_v08.json` for exact executed counts and qualifiers. Testing covers signed contract tampering, out-of-scope tools, replay/expiry, denial of unsafe requests, real app trace persistence, secure synthetic demo mode, existing security/approval, FDA fixtures, evidence reconciliation, backend API and Chromium UI. No sponsor credentials, production rows, or real warehouse actions were used.

## IMPORTANT: Not verified or not completed

- **Official upstream Meterless Scout npm eval harness:** **NOT RUN.** Engine is an independent Python spec adaptation with working *local* tests, not the official TypeScript library, and cannot claim official 32-example upstream evaluation/conformance. Official spec: https://github.com/Meterless/Meterless/blob/main/engines/scout-intent/AGENTS.md ; execution contracts: https://github.com/Meterless/Meterless/blob/main/engines/scout-intent/docs/execution-contract.md . Internet to the upstream repo/npm packages was unavailable in the build container.
- **NVIDIA Nemotron live inference:** **NOT VERIFIED.** `NVIDIA_API_KEY` and entitled `NVIDIA_MODEL` not supplied. Existing mock tests validate request shape, fallback and hallucination rejection, not live provider quality.
- **Zetaris live tenant SQL:** **NOT VERIFIED.** Need authorized tenant, query path and read-only mapped tables. Existing tests cover schema/URL allowlist and projection under stub responses only.
- **FDA official API successful external sync:** **NOT VERIFIED in this build.** Code and tests exist; internet outbound unavailable. Historical FDA enforcement data is not a real-time public alert or complete recall lifecycle.
- **Actual LangGraph runtime:** **NOT VERIFIED.** The optional `langgraph` package could not be installed here because public package DNS could not be resolved. The tested native orchestrator is not renamed LangGraph.
- **Hosted deployment:** source and opt-in security configuration tests passed, but an actual Render/cloud deployment, TLS, secret management, operations, resilience, data persistence and independent security review were **NOT performed**.
- **Real inventory / physical food recall linkage:** **NOT PROVIDED**. No commercial or regulatory validation. Synthetic lots RB-071, RB-072, RB-073 and RB-090 remain fictional.
- **Submission:** no external GitHub publish, demo filming, public URL, sponsor checkoff or HackOS submit was undertaken.

## Release verdict

**V0.8 LOCAL DEVELOPMENT CANDIDATE: VERIFIED WITH EXTERNAL BLOCKERS. NOT FINAL, NOT PRODUCTION-READY, AND NOT CLAIMED FULLY SPONSOR-INTEGRATED.**

A passing local evaluation is evidence for the implementation, not proof of official sponsor acceptance or model accuracy in the field. See `V08_HUMAN_ACTIONS_BN.md` for human-owned steps.

## 24 Oct 2026: user-facing UI branding correction

The V0.8 label was incorrectly displayed as an app version. Removed it from login, footer and Agent Investigation header, while preserving truthful training/demo warnings. Fixed white-on-white "FoodRecall" login brand text. See `docs/UI_BRANDING_FIX.md`. This does not change the outstanding live sponsor access or production-readiness limitations.
