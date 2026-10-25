# V0.2 Research-to-Implementation Map (source-informed, limited scope)

**This file maps concepts to actual V0.2 code only; it does not assert a reproduced paper result or globally novel algorithm.**

| Source | Relevant contribution | Implemented in V0.2 | NOT implemented / testing gap |
|---|---|---|---|
| Pulita, Pereira, Silva (2024), *How does traceability support stakeholders in food recall management?* (uploaded 101780.pdf; Table 1 on page 3) | Traceability before, during and after recall: source/supplier records, affected lot scoping, downstream tracking and post-recall review | Separate regulator source archive and staged event/lots, explicit original provenance | No real firm supplier data or traceability integration; no claims of reduced recall times |
| GS1 EPCIS 2.0 standard (uploaded download.pdf) | Standard event dimensions / ObjectEvent, bizStep, eventTime, business location, EPC identifiers | `data/synthetic_epcis_events.json` + `backend/traceability.py`: event records, graph projection, limited validation and negative tests | Not full GS1 certification, capture/query service, schema artefact validation or verified inventory cross-link |
| EventRAG (ACL 2025) | Event-centric representation and temporally related retrieval | Event chronology / explicit links in synthetic events, provenance-carrying graph projection | No retrieval agent, vector index, event knowledge augmentation or LLM multi-hop loop until V0.3 |
| Zep temporal knowledge graph (2025) | Validity, evidence histories, evolving facts | FDA raw snapshots + version ledger keyed by recall_number, first/last observation and content hashes | No semantic validity intervals or Graphiti infrastructure |
| SodaMem (2026 preprint) | Provenance and explicit temporal supersession | Simple source-linked versioning / observation times; conservative no-match decision | No full FactEvent graph, learned memory or formal supersession edges |
| RAGAs (EACL 2024) | Faithfulness/context/answer relevance evaluation framework | Not used at V0.2; identified future V0.3/Final evaluation design | No false RAG scores reported |

**Engineering decision:** a small local transactional SQLite data foundation provides deterministic provenance with minimal infra risk. It is intentionally not an artificial “AI graph reasoning” claim. Future investigation work must evaluate evidence-bound revalidation against a baseline, rather than merely calling source hash changes novel.
