"""Opt-in real live sponsor probes. Never prints credentials or returned business rows.

Run only with privately configured environment variables. A model text reply is NOT
proof of model-directed tool use; --nvidia-tools must be run separately.
"""
import argparse, json, os, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.agent_v03 import NVIDIAClient, ProviderError, tool_schema
from backend.zetaris import active_client, ZetarisError
from backend.sponsor_evidence import project_sources
p=argparse.ArgumentParser(description='Opt-in real sponsor endpoint tests (no secret output)')
p.add_argument('--nvidia',action='store_true',help='Live model text response')
p.add_argument('--nvidia-tools',action='store_true',help='Live model-selected tool calls (model-dependent)')
p.add_argument('--zetaris',action='store_true',help='Live tenant query, two source row parsers')
p.add_argument('--zetaris-ping',action='store_true',help='Local JDBC connection SELECT 1, no table data')
a=p.parse_args()
if not (a.nvidia or a.nvidia_tools or a.zetaris or a.zetaris_ping):p.error('Select --nvidia, --nvidia-tools and/or --zetaris')
results={}
if a.nvidia or a.nvidia_tools:
    try:
        client=NVIDIAClient()
        if a.nvidia:
            answer=client.complete([{'role':'user','content':'Reply with exactly READY.'}])
            results['nvidia_text']={'status':'LIVE_RESPONSE_OBSERVED' if answer.get('content') else 'UNVERIFIED_EMPTY_RESPONSE',
                                    'model':client.model,'content_present':bool(answer.get('content'))}
        if a.nvidia_tools:
            answer=client.complete([
                {'role':'system','content':'Select tool calls only. Do not return a text answer.'},
                {'role':'user','content':'Call the case_notice read-only tool now.'}],tools=tool_schema())
            names=[(t.get('function') or {}).get('name') for t in answer.get('tool_calls',[]) if isinstance(t,dict)]
            good='case_notice' in names
            results['nvidia_tool_calls']={'status':'LIVE_TOOL_CALL_OBSERVED' if good else 'BLOCKED_NO_VALID_TOOL_CALL',
                                          'model':client.model,'returned_tool_names':names[:6]}
    except ProviderError as e:
        results['nvidia']={'status':'BLOCKED','error':str(e)}
if a.zetaris_ping:
    try:
        from backend.zetaris_jdbc import ZetarisJDBCClient
        result=ZetarisJDBCClient().ping()
        results['zetaris_ping']={'status':result['status'],'rows_observed':result['rows_observed']}
    except (ZetarisError,ValueError):
        results['zetaris_ping']={'status':'BLOCKED','error':'Local JDBC ping failed (verify Java, jar, and private credentials)'}
if a.zetaris:
    try:
        client=active_client()
        raw=client.read_approved_sources()
        projected=project_sources(raw)
        sources=projected['sources']
        fully_parsed=all(s['response_parsed'] for s in sources.values())
        results['zetaris']={'status':'LIVE_ROWS_PARSED' if fully_parsed else 'LIVE_RESPONSE_UNRECOGNIZED_SCHEMA',
                           'sources':{name:{'row_count':src['row_count'],'response_parsed':src['response_parsed']} for name,src in sources.items()},
                           'verified_inventory_linkage':False}
    except (ZetarisError,ValueError) as e:
        results['zetaris']={'status':'BLOCKED','error':type(e).__name__+' (review tenant URL, token, query path and mappings)'}
print(json.dumps(results,ensure_ascii=False,indent=2))
sys.exit(0 if results and all(v['status'] in ('LIVE_RESPONSE_OBSERVED','LIVE_TOOL_CALL_OBSERVED','LIVE_ROWS_PARSED','LIVE_SELECT1_OBSERVED') for v in results.values()) else 2)
