"""Secret-safe, reproducible readiness report. Never proves live use from env flags.

python scripts/preflight.py --output verification/PREFLIGHT_LOCAL.json
python scripts/preflight.py --live --output verification/PREFLIGHT_LIVE_LOCAL.json

The second form makes outbound provider requests and must only be run with
privately authorized credentials; never attach the private env file to a ZIP.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
PROBES={
    'nvidia':('NVIDIA_API_KEY','NVIDIA_MODEL'),
    'zetaris':('ZETARIS_URL','ZETARIS_ID_TOKEN','ZETARIS_QUERY_PATH','ZETARIS_RECALL_TABLE','ZETARIS_SHIPMENT_TABLE'),
    'meterless':('METERLESS_BASE_URL','METERLESS_API_KEY','METERLESS_MODEL'),
}

def build_report(live=False):
    report={
        'generated_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'artifact':'FoodRecall AI v0.8 local integration readiness',
        'scope':'LOCAL TRAINING, not enterprise certified / not a public deployment',
        'checks':{},'live_tests':{},
    }
    checks=report['checks']
    for provider,keys in PROBES.items():
        if provider == 'zetaris' and os.getenv('ZETARIS_MODE', 'https').lower() == 'jdbc':
            keys=('ZETARIS_JDBC_JAR','ZETARIS_JDBC_USER','ZETARIS_JDBC_PASSWORD','ZETARIS_RECALL_TABLE','ZETARIS_SHIPMENT_TABLE')
        configured=all(bool(os.environ.get(k)) for k in keys)
        checks[provider]={'configuration':'PRESENT_NOT_VERIFIED' if configured else 'MISSING',
                          'required_variable_names':list(keys)}
    checks['zetaris']['connection_mode']=os.getenv('ZETARIS_MODE','https').lower()
    checks['langgraph']={'status':'IMPORT_AVAILABLE_NOT_RUNTIME_VERIFIED' if importlib.util.find_spec('langgraph') else 'NOT_INSTALLED'}
    from backend import scout_intent
    checks['scout_intent']={'status':'IMPLEMENTED_LOCAL_TESTABLE_NOT_OFFICIAL_CONFORMANCE',
        'implementation':'scoped Python Scout Intent in agent planner and signed executor',
        'stage1_selftest':scout_intent.selftest(),
        'upstream_npm_evals':'NOT_EXECUTED'}
    checks['coding_tool']={'status':'USER_CONFIRMATION_OPTIONAL','note':'Cursor optional per organizer update supplied by participant.'}
    checks['docker']={'status':'CLI_FOUND_NOT_ENGINE_VERIFIED' if shutil.which('docker') else 'CLI_NOT_FOUND'}
    checks['external_data_linkage']={'status':'NOT_VERIFIED','note':'No authorized operational inventory link; exact joins are review candidates only.'}
    checks['public_deployment']={'status':'NOT_PRODUCTION_READY',
        'note':'Explicit opt-in HTTPS single-tenant synthetic demo mode exists; hosting/TLS/security not live verified. Not for real inventory.'}
    checks['fda']={'status':'NO_LIVE_SYNC_VERIFIED','note':'Requires authenticated local app FDA sync and real successful result.'}
    if live:
        # Do not log raw provider responses or secrets. Exact statuses are issued
        # by the existing read-only probe, with server-owned table mappings.
        requested=[]
        if checks['nvidia']['configuration']=='PRESENT_NOT_VERIFIED':requested+=['--nvidia','--nvidia-tools']
        if checks['zetaris']['configuration']=='PRESENT_NOT_VERIFIED':requested+=['--zetaris']
        if requested:
            try:
                p=subprocess.run([sys.executable,str(ROOT/'scripts/check_live_integrations.py'),*requested],
                                 capture_output=True,text=True,timeout=100,cwd=str(ROOT))
                data=json.loads(p.stdout)
                # Strict allowlist prevents provider error strings from being saved.
                for k,v in data.items():
                    report['live_tests'][k]={'status':v.get('status','UNVERIFIED'),
                       **({'model_tool_calls':v.get('returned_tool_names',[])[:6]} if k=='nvidia_tool_calls' else {}),
                       **({'source_row_counts':{name:info.get('row_count') for name,info in v.get('sources',{}).items()}} if k=='zetaris' else {})}
            except (ValueError,subprocess.TimeoutExpired,OSError):
                report['live_tests']['provider_probes']={'status':'UNVERIFIED_PROBE_ERROR'}
        else:report['live_tests']['providers']={'status':'BLOCKED_NO_CONFIG'}
    report['release_verdict']='NOT_PRODUCTION_READY'
    report['required_human_dependencies']=['Provision authorized Zetaris instance and data sources',
      'Choose entitled NVIDIA Nemotron model and private API key',
      'Verify real LangGraph runtime on internet-connected host',
      'Run upstream Meterless Scout Intent harness or obtain sponsor confirmation of Python spec + local test acceptance',
      'Authorize external deployment/GitHub submission and film an actual verified demo']
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true',help='explicitly opt into external NVIDIA/Zetaris API calls')
    parser.add_argument('--output',type=Path,help='Save report as JSON (never save credentials)')
    args=parser.parse_args()
    report=build_report(live=args.live)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
