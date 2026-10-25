"""Reproducible SYNTHETIC evidence-dependency regression benchmark.

This uses real SQLite and production decision functions, but NO external FDA,
NVIDIA, Zetaris, LLM, or public deployment; it is a unit stress test, not a
real-world recall accuracy/precision/recall measurement.
"""
from __future__ import annotations
import json, os, statistics, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
api=None
decision_v04=None

SPEC=json.loads((ROOT/'evaluation/ground_truth_scenarios.json').read_text(encoding='utf-8'))


def modify(c,category,variant):
    tag=str(variant)
    if category=='material_lot_quantity':
        c.execute('UPDATE lots SET quantity=quantity+? WHERE id="RB-071"',(variant+1,))
    elif category=='material_lot_location':
        c.execute('UPDATE lots SET location=? WHERE id="RB-071"',('Zone-'+tag,))
    elif category=='material_lot_classification':
        c.execute('UPDATE lots SET classification="uncertain" WHERE id="RB-072"')
    elif category=='material_new_affected_lot':
        c.execute('UPDATE lots SET classification="affected" WHERE id="RB-090"')
    elif category=='material_notice_detail':
        c.execute('UPDATE evidence SET detail=detail||? WHERE id="E-01"',(' revision '+tag,))
    elif category=='material_notice_version':
        c.execute('UPDATE evidence SET version=version+? WHERE id="E-01"',(variant+1,))
    elif category=='material_critical_addition':
        c.execute('INSERT INTO evidence VALUES (?,?,?,?,?,?,?)',('E-NEW','DEMO-001','supplier_response','New critical',tag,1,'Synthetic fixture'))
    elif category=='material_uncertain_lot_resolved':
        c.execute('UPDATE lots SET classification="clear" WHERE id="RB-073"')
    elif category=='noncritical_note_insert':
        c.execute('INSERT INTO evidence VALUES (?,?,?,?,?,?,?)',('E-NOTE','DEMO-001','analyst_note','New note',tag,1,'Synthetic fixture'))
    elif category=='noncritical_note_revision':
        c.execute('INSERT INTO evidence VALUES (?,?,?,?,?,?,?)',('E-NOTE','DEMO-001','analyst_note','Note',tag,variant+2,'Synthetic fixture'))
    elif category=='noncritical_case_title':
        c.execute('UPDATE cases SET title=? WHERE id="DEMO-001"',('Presentation title '+tag,))
    elif category=='noncritical_audit_entry':
        api.audit(c,'test_annotation',{'variant':variant})
    elif category=='noncritical_clear_inventory_quantity':
        c.execute('UPDATE lots SET quantity=quantity+? WHERE id="RB-090"',(variant+1,))
    else:
        raise ValueError('Unknown benchmark category')


def main():
    global api, decision_v04
    out=[]
    with tempfile.TemporaryDirectory(prefix='foodrecall-eval-') as temp:
        original_db_env=os.environ.get('FOODRECALL_DB')
        os.environ['FOODRECALL_DB']=str(Path(temp)/'evaluation.sqlite')
        # This benchmark never creates or exposes real login credentials.
        previous={k:os.environ.get(k) for k in ('FOODRECALL_BOOTSTRAP_PASSWORD','FOODRECALL_ANALYST_PASSWORD')}
        os.environ['FOODRECALL_BOOTSTRAP_PASSWORD']='Evaluation_Only_Test_QA_2026'
        os.environ['FOODRECALL_ANALYST_PASSWORD']='Evaluation_Only_Test_Analyst_2026'
        try:
            from backend import app as api, decision_v04
            api.initialize()
            for category in SPEC['scenario_categories']:
                for variant in range(SPEC['variants_per_category']):
                    api.reset(api.ResetBody(confirm='RESET_DEMO'))
                    proposal=api.make_proposal('DEMO-001')['id']
                    with api.db() as c:
                        before=decision_v04.compare(c,api.load_proposal(c,proposal))
                        assert before['current'],(category['name'],'invalid initial proposal')
                        modify(c,category['name'],variant)
                        p=api.load_proposal(c,proposal)
                        start=time.perf_counter()
                        diff=decision_v04.compare(c,p)
                        millis=(time.perf_counter()-start)*1000
                    expected=category['expected_current']
                    out.append({'category':category['name'],'variant':variant,
                                'expected_current':expected,'actual_current':diff['current'],
                                'passed':diff['current']==expected,'latency_ms':round(millis,4),
                                'changes':len(diff['changes'])})
        finally:
            if original_db_env is None:os.environ.pop('FOODRECALL_DB',None)
            else:os.environ['FOODRECALL_DB']=original_db_env
            for key,value in previous.items():
                if value is None:os.environ.pop(key,None)
                else:os.environ[key]=value
    passed=sum(x['passed'] for x in out)
    lengths=sorted(x['latency_ms'] for x in out)
    report={'evaluation_name':SPEC['dataset_name'],'timestamp':datetime.now(timezone.utc).isoformat(),
            'origin':SPEC['origin'],'scope':'Single-tenant synthetic decision dependency regression only',
            'test_method':'Real isolated SQLite, deterministic production functions, manually specified ground truth; no external APIs',
            'total':len(out),'passed':passed,'failed':len(out)-passed,
            'safety_property_violations':sum(not x['passed'] for x in out),
            'latency_ms_p50':round(statistics.median(lengths),4),
            'latency_ms_p95':lengths[max(0,int(len(lengths)*.95)-1)],
            'live_fda_tested':False,'live_nemotron_tested':False,'live_zetaris_tested':False,
            'llm_faithfulness_measured':False,'product_lot_precision_recall_measured':False,
            'scenarios':out}
    output=ROOT/'evaluation/results_evidence_dependencies.json'
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f"SYNTHETIC EVIDENCE-DEPENDENCY EVAL: {passed}/{len(out)} pass, p50={report['latency_ms_p50']} ms, p95={report['latency_ms_p95']} ms")
    print('Results:',output)
    return 0 if passed==len(out) else 1

if __name__=='__main__':sys.exit(main())
