# V0.4 — Local Security + Temporal Decision Validity Architecture

- **Trust boundaries:** Untrusted frontend, untrusted FDA & supplier content, session cookie validated per write, cookie-CSRF double verification, deterministic policy authorization; no LLM agent has mutation tools.
- **Actors:** QA manager creates/approves/executes/reset/revisions; analyst can propose/investigate/sync; auditor only reads. These are LOCAL training accounts. The `X-Demo-Role` header is ignored.
- **Identity:** Salted PBKDF2-SHA256 passwords (260k iterations); 5 failures → 10-minute lock, expiring 8-hour hashed session tokens; HttpOnly/SameSite=strict cookie; fresh CSRF token required on each write. Auth audit event records no secrets.
- **Approval provenance:** Each new proposal carries an immutable `proposal_dependencies` snapshot of selected critical evidence versions and all affected/uncertain lot scope. Hash = SHA256(canonical JSON). Material differences fail closed and block before execution. Readback reconciles lots, idempotent action receipts.
- **Irrelevant changes:** ordinary `analyst_note` updates do not automatically stale an existing approval. If future new evidence kinds affect safety, add to `CRITICAL_KINDS` and test before use. There is no automatic semantic determination of a document's significance.
- **Legacy migration:** V0.3 proposals lack V0.4 dependencies; all fail closed until recreated. No unverifiable migration of prior authorizations.
- **Race limits:** Single-process `DB_LOCK` and `BEGIN IMMEDIATE` on execution. Not proven safe for horizontal multi-worker production deployment. Cross-process concurrency, tenant isolation, enterprise IAM, encrypted backup, immutable remote audit and legal/compliance audit are future work.
- **Non-agent authority:** Model/agent endpoints expose only readonly allowlisted tools; FDA recalls and synthetic EPCIS events do NOT prove real warehouses contain affected lots.
