"""V0.7 regression: real local SQLite, fake inference only (never claim live)."""
import json
from backend import answer_v07, agent_v03
from backend import app as api
from backend.tests.auth_support import AuthClient


def test_user_questions_get_distinct_evidence_scoped_answers(tmp_path, monkeypatch):
    monkeypatch.setattr(api,'DB_PATH',str(tmp_path/'intents.sqlite'))
    api.initialize()
    client=AuthClient(api.app)
    affected=client.post('/api/agent/chat',json={'message':'Which lots are affected?'}).json()
    conflict=client.post('/api/agent/chat',json={'message':'Why is the supplier evidence uncertain?'}).json()
    actions=client.post('/api/agent/chat',json={'message':'What should we do next?'}).json()
    assert len({affected['answer'],conflict['answer'],actions['answer']})==3
    assert affected['intent']=='affected'
    assert conflict['intent']=='uncertain'
    assert actions['intent']=='action'
    assert all(r['training_only'] and r['write_actions_taken']==0 for r in (affected,conflict,actions))
    assert 'RB-073' in conflict['answer'] and '[E-03]' in conflict['answer']
    assert all(r['response_mode']=='verified_rules_offline' for r in (affected,conflict,actions))


def test_bangla_grounded_response_and_saved_locale(tmp_path, monkeypatch):
    monkeypatch.setattr(api,'DB_PATH',str(tmp_path/'bn.sqlite'))
    api.initialize()
    client=AuthClient(api.app)
    r=client.post('/api/agent/chat',json={'message':'কোন লট ঝুঁকিতে আছে?', 'language':'bn','thread_id':'one'}).json()
    assert 'কাল্পনিক' in r['answer']
    assert 'RB-071' in r['answer'] and 'RB-072' in r['answer']
    assert r['language']=='bn'
    with api.db() as c:
        saved=c.execute('SELECT language FROM agent_runs WHERE id=?',(r['run_id'],)).fetchone()
    assert saved['language']=='bn'


def test_model_explanation_used_only_with_existing_citations_and_canonical_summary(tmp_path, monkeypatch):
    monkeypatch.setattr(api,'DB_PATH',str(tmp_path/'model.sqlite'))
    api.initialize()
    class StubModel:
        ready=True
        def __init__(self):self.calls=0
        def complete(self, messages, tools=None):
            self.calls+=1
            if tools:
                return {'tool_calls':[{'function':{'name':'case_notice','arguments':'{}'}},
                                      {'function':{'name':'inventory_lots','arguments':'{}'}},
                                      {'function':{'name':'supplier_evidence','arguments':'{}'}}]}
            return {'content':json.dumps({'answer':'Supplier records are incomplete [E-03], so RB-073 cannot be cleared without review.',
                                          'citations':['E-03']})}
    model=StubModel()
    res=agent_v03.run('Why is RB-073 uncertain?','DEMO-001',api.db,model=model,engine='native',language='en')
    assert model.calls==2
    assert res['model_response_status']=='passed_syntactic_guard_not_fact_certification'
    assert res['response_mode']=='source_summary_plus_model_explanation'
    assert 'TRAINING DATA ONLY' in res['answer'] and 'AI explanation' in res['answer']
    assert res['confirmed_units']==205 and res['write_actions_taken']==0


def test_hallucinated_lot_reference_falls_back_to_grounded_rules(tmp_path,monkeypatch):
    monkeypatch.setattr(api,'DB_PATH',str(tmp_path/'reject.sqlite'))
    api.initialize()
    class Fake:
        ready=True
        def complete(self,messages,tools=None):
            if tools:return {'tool_calls':[{'function':{'name':'case_notice','arguments':'{}'}},
                                          {'function':{'name':'inventory_lots','arguments':'{}'}}]}
            return {'content':json.dumps({'answer':'A genuine dangerous lot RB-999 was located [E-01] and a warehouse was held.',
                                         'citations':['E-01']})}
    r=agent_v03.run('Find risky lots','DEMO-001',api.db,model=Fake(),engine='native')
    assert r['model_response_status']=='rejected_by_output_guard'
    assert 'RB-999' not in r['answer']
    assert r['response_mode']=='verified_rules_offline'
    assert r['write_actions_taken']==0


def test_invented_citations_and_numbers_are_rejected():
    facts={'citations':[{'id':'E-01'}],'confirmed_lots':['RB-071'],'uncertain_lots':['RB-073'],
           'confirmed_units':205,'uncertain_units':46}
    for body,refs in [('The report proves 999 units are affected [E-01].',['E-01']),
                      ('Unknown company invoice [X-10] controls recall decisions.',['X-10']),
                      ('We have executed a warehouse hold [E-01].',['E-01'])]:
        assert answer_v07.accept_model_explanation({'content':json.dumps({'answer':body,'citations':refs})},facts) is None


def test_account_thread_namespaces_do_not_overlap(tmp_path,monkeypatch):
    monkeypatch.setattr(api,'DB_PATH',str(tmp_path/'scope.sqlite'))
    api.initialize()
    qa=AuthClient(api.app,role='qa_manager')
    analyst=AuthClient(api.app,role='analyst')
    a=qa.post('/api/agent/chat',json={'message':'Why?', 'thread_id':'shared_screen'}).json()
    b=analyst.post('/api/agent/chat',json={'message':'Why?', 'thread_id':'shared_screen'}).json()
    assert a['thread_id']==b['thread_id']=='shared_screen'
    with api.db() as c:
        scope=[r['thread_id'] for r in c.execute('SELECT thread_id FROM agent_threads ORDER BY id')]
    assert len(set(scope))==2
    assert all('shared_screen' in x for x in scope)


def test_non_english_followup_stays_training_scoped():
    assert answer_v07.intent_for('কেন?', ['আমার কোন লট অনিশ্চিত?'])=='uncertain'
    assert answer_v07.intent_for('What about that?', ['Where is the shipment?'])=='overview'


def test_new_supplier_evidence_changes_live_answer_and_revalidation(tmp_path,monkeypatch):
    monkeypatch.setattr(api,'DB_PATH',str(tmp_path/'revise.sqlite'))
    api.initialize();client=AuthClient(api.app)
    before=client.post('/api/agent/chat',json={'message':'Which lots are uncertain?'}).json()
    assert before['uncertain_lots']==['RB-073']
    revised=client.post('/api/cases/DEMO-001/simulate-revision',json={'confirm':'SIMULATE'})
    assert revised.status_code==200
    after=client.post('/api/agent/chat',json={'message':'Which lots are uncertain?'}).json()
    assert after['uncertain_lots']==[] and 'No unresolved lots' in after['answer']
    assert 'batch log is incomplete' not in after['answer']
    changed=client.post('/api/agent/chat',json={'message':'What changed?'}).json()
    assert changed['intent']=='change'
    assert 'revision: 2' in changed['answer']
    assert '[E-03] v2' in changed['answer']
    assert changed['write_actions_taken']==0
