# FoodRecall AI

**Evidence-Grounded Food Recall Investigation & Explainable Decision Support**

FoodRecall AI is a food-recall investigation workbench designed to help users review recall evidence, understand product and shipment traceability, and make explainable decisions with human oversight.

Built for **Open Agent Hackathon 2026** by **Team SynonymS**.

**[Open Live Demo](https://foodrecall-ai-demo.onrender.com)** | **[GitHub Repository](https://github.com/sadia-zannat/FoodRecall-AI)**

**Demo availability:** Render deployment succeeded and the QA Manager signed in successfully on 26 October 2026. The hosted site is a controlled synthetic training workspace; the full investigation and approval flow still needs an end-to-end hosted acceptance run.

> **Public demo uses fictional training data.** It is not a certified food-safety service or a verified link to a real company's inventory.

## The Problem

Food recall investigations involve fragmented notices, product lots, suppliers, shipments, and warehouse records. Missing or conflicting evidence makes it difficult to establish which items are affected and why a decision should be trusted.

## What FoodRecall AI Does

- **Investigation workspace:** Explore cases and related evidence.
- **Evidence-aware explanations:** Examine the basis for a finding instead of relying on unsupported claims.
- **Traceability review:** See available relationships among products, lots, shipments, and locations.
- **PASS / REVIEW / BLOCK decision support:** Distinguish supported conclusions, uncertainty, and significant conflicts.
- **Human-in-the-loop workflow:** Review and approve simulated actions; reassess approvals when critical evidence changes.
- **Auditability:** Retain an investigation trail and distinguish training records from verified external sources.

## Workflow

1. Open a recall investigation or submit a question.
2. Inspect the available notice, lot, supplier, and shipment evidence.
3. Analyze consistency, missing links, and decision dependencies.
4. Review the rationale for PASS, REVIEW, or BLOCK.
5. Have an authorized user review simulated actions and audit the outcome.

## Architecture

```text
Web interface (HTML / CSS / JavaScript)
                 |
             FastAPI API
                 |
       Investigation workflow
        /         |          \
 Evidence     Decision      Audit and
 review       validity      approvals
        \         |          /
           SQLite demo data

Optional integrations: FDA connector, Zetaris SQL/JDBC,
and an LLM adapter (see verified status below).
```

**Stack:** Python, FastAPI, HTML/CSS/JavaScript, SQLite, Docker, pytest, GitHub Actions, Render.

## Verified Status and Limitations

| Area | Current status |
| --- | --- |
| GitHub source code | Published |
| Render hosted demo | Deployed; health endpoint returned HTTP 200 |
| Hosted QA Manager sign-in | Verified by a screenshot of the authenticated Overview page (26 October 2026) |
| Hosted investigation and full approval workflow | Not yet independently verified end-to-end |
| Local Zetaris JDBC | Live `SELECT 1` and `default` catalog access observed |
| Zetaris recall and shipment investigation | Not yet verified end-to-end |
| FDA live ingestion | Not yet verified end-to-end |
| NVIDIA Nemotron / Meterless live inference | Not yet verified |
| Operational inventory actions | Synthetic training simulation only |


FoodRecall AI has successfully established and verified a live local JDBC connection to Zetaris, including a successful SQL `SELECT 1` query and `default` catalog discovery.

End-to-end recall and shipment data integration remains under development. The public Render demo currently operates independently using synthetic training data.

A functioning connector or local test does not prove full external source integration.

For detailed technical documentation and evidence, see [Sponsor Integration Report](SPONSOR_INTEGRATION_REPORT.md) and [Development Changelog](CHANGELOG.md).

## Run Locally

Requires Python 3.10+; Python 3.12 is recommended. On Windows, run `RUN_WINDOWS.bat` from the project root or use:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. First startup provisions QA and analyst training accounts. Keep all credentials private.

Run backend tests:

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q
```

## Hosted Demo Access

**https://foodrecall-ai-demo.onrender.com**

The hosted workbench uses provisioned accounts; **there is no public Register / Sign up option**.

**For hackathon judges**

1. Open the [Live Demo](https://foodrecall-ai-demo.onrender.com).
2. Sign in with a **temporary, separately provisioned evaluator account** shared privately by Team SynonymS. The team must configure and test such an account before promising access; it is not yet confirmed to exist.
3. Review the Overview, Investigation, Agent investigation, Traceability explorer, Approvals & actions, and Activity log sections. Only test the features and controls available to the account.
4. All cases, lot counts, risk decisions, and holds in the hosted demo are **fictional training records**.

**Current internal login:** `qa@local.foodrecall` is a QA Manager account, **not a public evaluation account**. Never put its password—or the analyst password—into a public README. Grant judges limited-access credentials through a private submission communication or implement a safe read-only demo account before distributing access publicly.

On Render Free, the service may sleep when inactive, and the temporary SQLite database may reset on restart. See [Hosted Demo Security Guide](docs/SAFE_HOSTED_TRAINING_DEMO.md).

## Screenshots

Screenshots of the application are available in the repository, including `SCREENSHOT_overview.png`, `SCREENSHOT_investigation.png`, `SCREENSHOT_traceability.png`, and `SCREENSHOT_v07_agent_investigation.png`. These are illustrative development captures, not a substitute for demonstrating the currently hosted build.

## Development Notes

FoodRecall AI is **one project**. Earlier version numbers were development checkpoints for tracking fixes and tests, not separate products. Historical technical logs are kept in [CHANGELOG.md](CHANGELOG.md), rather than being used as the public project title.

## Responsible Use

This prototype uses fictional food-recall evidence and simulated inventory. It is not suitable for real product release, recall execution, or regulatory decisions without independent verification and qualified human review. Do not commit passwords, tokens, `.env` files, or real private inventory data.

## Team

**SynonymS** — Open Agent Hackathon 2026, *The Agent That Can Explain Why*

- **Sadia Akter Zannat** — Team Lead
- **Md. Nazrul Islam Leon** — Team Member

[Live Demo](https://foodrecall-ai-demo.onrender.com) | [GitHub Source](https://github.com/sadia-zannat/FoodRecall-AI)
