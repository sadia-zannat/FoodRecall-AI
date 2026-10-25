"""Regression for user-reported multi-part question; all records remain training-only."""
from backend import answer_v07, agent_v03
from backend import app as api
from backend.tests.auth_support import AuthClient

QUESTION=('Which lots are affected, which lots remain uncertain, '
          'and what evidence supports these classifications?')


def test_combined_question_local_http_returns_both_groups_and_lot_level_sources(tmp_path, monkeypatch):
    monkeypatch.setattr(api,'DB_PATH',str(tmp_path/'combined.sqlite'))
    api.initialize()
    client=AuthClient(api.app)
    result=client.post('/api/agent/chat',json={'message':QUESTION,'thread_id':'multi_question'}).json()
    assert result['intent']=='lot_status_evidence'
    assert result['response_mode']=='verified_rules_offline'
    assert result['confirmed_lots']==['RB-071','RB-072']
    assert result['uncertain_lots']==['RB-073']
    assert result['confirmed_units']==205 and result['uncertain_units']==46
    assert 'RB-071 (120 units)' in result['answer']
    assert 'RB-072 (85 units)' in result['answer']
    assert 'RB-073 (46 units)' in result['answer']
    assert 'Retrieved records mentioning RB-071: [E-01], [E-02]' in result['answer']
    assert 'Retrieved records mentioning RB-073: [E-02], [E-03]' in result['answer']
    assert 'Source mentions and shipment counts are not independent proof' in result['answer']
    assert result['write_actions_taken']==0 and result['training_only']
    assert len(result['trace'])>=1
    assert result['run_id'].startswith('run_')
    saved=client.get('/api/agent/runs/'+result['run_id'])
    assert saved.status_code==200


def test_combined_question_changes_after_supplier_revision(tmp_path, monkeypatch):
    monkeypatch.setattr(api,'DB_PATH',str(tmp_path/'revision.sqlite'))
    api.initialize()
    client=AuthClient(api.app)
    before=client.post('/api/agent/chat',json={'message':QUESTION}).json()
    assert before['uncertain_lots']==['RB-073']
    rev=client.post('/api/cases/DEMO-001/simulate-revision',json={'confirm':'SIMULATE'})
    assert rev.status_code==200
    after=client.post('/api/agent/chat',json={'message':QUESTION}).json()
    assert after['confirmed_lots']==['RB-071','RB-072','RB-073']
    assert after['uncertain_lots']==[]
    assert 'Still uncertain: none' in after['answer']
    assert 'Retrieved records mentioning RB-073: [E-02], [E-03]' in after['answer']
    assert after['write_actions_taken']==0


def test_multilingual_combined_question_and_normal_single_intent():
    assert answer_v07.intent_for('Which lots are affected and uncertain?')=='lot_status_evidence'
    assert answer_v07.intent_for('Which affected lots have supporting evidence?')=='lot_status_evidence'
    assert answer_v07.intent_for('কোন লট আক্রান্ত, কোন লট অনিশ্চিত, এবং প্রমাণ কী?')=='lot_status_evidence'
    assert answer_v07.intent_for('Which lots are affected?')=='affected'
    assert answer_v07.intent_for('Why is RB-073 uncertain?')=='uncertain'


def test_missing_inventory_or_source_does_not_invent_evidence():
    absent=answer_v07.make_answer(QUESTION,{},'DEMO-001')
    assert absent['insufficient_context'] is True
    assert 'inventory data was not retrieved' in absent['answer']
    assert 'RB-071' not in absent['answer']
    partial=answer_v07.make_answer(QUESTION,{'inventory_lots':{
        'lots':[{'id':'RB-071','quantity':120,'classification':'affected'},
                {'id':'RB-073','quantity':46,'classification':'uncertain'}]}},'DEMO-001')
    assert partial['citations']==[]
    assert 'No retrieved source record specifically mentions RB-071' in partial['answer']
    assert '[E-01]' not in partial['answer'] and '[E-03]' not in partial['answer']
