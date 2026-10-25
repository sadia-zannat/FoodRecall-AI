# Open Source / Reuse Audit — V0.2

- **Source copied into this project from third-party GitHub libraries:** NONE. No GitHub libraries were vendored; V0.2 code is newly authored to follow official public API field documentation and GS1 concepts.
- **Runtime dependencies:** FastAPI, Uvicorn, pytest, httpx. Version ranges documented in `backend/requirements.txt`. Use `pip show` or pin resolved versions before final judging.
- **Conceptual references only:** FDA/openfda, OpenEPCIS test resources, OpenEPCIS generator, LangGraph, Graphiti, Microsoft GraphRAG, RAGAs and SodaMem (as described in user's master prompt). No repository was cloned/used as a software dependency or represented as integrated.
- **GS1 standard:** standards document consulted; EPCIS-shaped fixture is authored from public field names/URIs. Not a certified implementation.
- **Research papers:** cited as architectural influences in `RESEARCH_TO_IMPLEMENTATION.md` rather than recycled code or reproduced benchmarks.
- **When V0.3 adds dependencies:** check each repository's actual LICENSE, record precise version/commit, license compatibility, attribution and reasons for use.
