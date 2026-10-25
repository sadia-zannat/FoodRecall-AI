# V0.3 architecture and security contracts

```
Agent Lab / Assistant
  -> POST /api/agent/chat  (read-only, local training)
  -> Model selector (NVIDIA Nemotron OR configured Meterless gateway)
     -> validated function call names / empty argument objects only
     -> if model unavailable: RULE-SELECTED OFFLINE mode, loudly labeled
  -> Planner -> Tool executor -> Evidence evaluator -- missing source? --> Planner
                              -> Reporter (only facts from tools)
  -> SQLite agent_runs + agent_trace + agent_threads (evidence, run_id, observable events)
  -> UI source evidence + accurate mode label
```

When LangGraph is installed, the intended orchestration is a LangGraph `StateGraph` with explicit conditional evaluation and loop. In this build environment it was **not run**. The native runtime implements the same step order but MUST NOT be called LangGraph.

Actual allowlisted tools: case_notice, inventory_lots, supplier_evidence, cached_fda, synthetic_epcis, zetaris_sources. No LLM exposes SQL strings, writes, approval, proposal creation, release, reset or inventory mutations. All evidence metadata sent to end users has synthetic/official-cache labels. Missing table/data results never imply a real FDA-to-warehouse lot relationship. Source hashes/versions remain from V0.2.

Citations: every cited `E-..` is read from the training case's evidence table; no free-form, unverified model response is sent as a factual authoritative answer. Model used for *tool selection*, not direct inventory write policy. Reports carry `selection_mode`, `graph_engine`, `run_id`, `mode_warning`, `citations` and `trace`. Tool trace is independently persisted as SQLite events and contains no proprietary model chain of thought.

Unresolved: actual LangGraph runtime; live Nemotron tools, Zetaris connectivity, external-source provenance in a live query; auth/multi-tenancy. Do not deploy publicly.
