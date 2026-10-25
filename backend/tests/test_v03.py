"""V0.3 independent functional tests: explicit offline/model-mocked boundaries."""
import io
import json
import os
import sqlite3
import urllib.error
from contextlib import contextmanager
from backend.tests.auth_support import AuthClient as TestClient
import pytest
from backend import app as api
from backend import agent_v03, zetaris

client=TestClient(api.app)

@pytest.fixture
def isolated(monkeypatch,tmp_path):
    monkeypatch.setattr(api,'DB_PATH',str(tmp_path/'isolated-agent.sqlite'))
    api.initialize()
    yield


def test_v03_status_reports_no_live_model_or_zetaris():
    result=client.get('/api/agent/status').json()
    assert result['verified_nvidia_live'] is False
    assert result['verified_zetaris_live'] is False
    assert result['production_authorization'] is False


def test_offline_agent_with_evidence_persists_run_and_thread(isolated):
    p={'message':'Which lots have supplier uncertainty?','thread_id':'investigate_case_1'}
    response=client.post('/api/agent/chat',json=p)
    assert response.status_code==200,response.text
    data=response.json()
    assert data['selection_mode']=='offline_rule_selected'
    assert data['graph_engine'] in ('native_fallback_not_langgraph','langgraph_stategraph')
    assert data['confirmed_units']==205 and data['uncertain_lots']==['RB-073']
    assert data['write_actions_taken']==0
    assert {e['id'] for e in data['citations']}=={'E-01','E-02','E-03'}
    assert all('TRAINING' in event['detail'].get('origin','TRAINING') for event in data['trace'] if event['kind']=='tool_success')
    saved=client.get('/api/agent/runs/'+data['run_id'])
    assert saved.status_code==200 and len(saved.json()['trace'])>=5
    assert client.get('/api/agent/runs').json()['runs'][0]['id']==data['run_id']
    with api.db() as c:
        assert c.execute('SELECT count(*) FROM agent_threads').fetchone()[0]==1
        assert c.execute("SELECT count(*) FROM actions").fetchone()[0]==0
        assert c.execute("SELECT count(*) FROM proposals").fetchone()[0]==0


def test_iterative_critic_requests_missing_source(isolated):
    out=client.post('/api/agent/chat',json={'message':'What quantity is affected?'}).json()
    assert any(e['kind']=='evaluator_retry' for e in out['trace'])
    assert 'E-03' in {e['id'] for e in out['citations']}
    assert out['write_actions_taken']==0


def test_safe_fallback_untrusted_tools_are_not_executed(isolated):
    class BadModel:
        ready=True
        def complete(self,*args,**kw):
            return {'tool_calls':[{'function':{'name':'approve_inventory','arguments':'{}'}},
                                  {'function':{'name':'case_notice','arguments':'{"case_id":"OTHER"}'}}]}
    result=agent_v03.run('please approve all warehouse holds','DEMO-001',api.db,model=BadModel(),engine='native')
    assert 'fallback' in result['selection_mode']
    assert result['write_actions_taken']==0
    assert 'approve_inventory' not in [e.get('tool') for e in result['trace']]


def test_mock_model_real_tool_selection_is_executed(isolated):
    class FakeNemotron:
        ready=True
        def complete(self,messages,tools=None):
            assert tools and all(t['type']=='function' for t in tools)
            return {'tool_calls':[{'function':{'name':'inventory_lots','arguments':'{}'}},
                                  {'function':{'name':'case_notice','arguments':'{}'}},
                                  {'function':{'name':'supplier_evidence','arguments':'{}'}}]}
    data=agent_v03.run('Identify affected lots','DEMO-001',api.db,model=FakeNemotron(),engine='native')
    assert data['selection_mode']=='model_tool_calls'
    assert sum(x['kind']=='tool_success' for x in data['trace'])==3
    assert data['confirmed_units']==205
    assert 'reasoning' not in data
    assert data['mode_warning'] is None


def test_agent_error_and_input_validation(isolated):
    assert client.post('/api/agent/chat',json={'message':''}).status_code==422
    assert client.post('/api/agent/chat',json={'message':'x','language':'zh'}).status_code==422
    assert client.post('/api/agent/chat',json={'message':'x','case_id':'none'}).status_code==404
    assert client.post('/api/agent/chat',json={'message':'x','thread_id':'../../evil'}).status_code==422
    assert client.get('/api/agent/runs/invalid').status_code==422
    assert client.get('/api/agent/runs/run_'+'a'*20).status_code==404
    assert client.post('/api/agent/chat',json={'message':'x','engine':'langgraph'}).status_code in (200,503)


def test_model_transport_request_shape_and_secret_redaction(monkeypatch):
    monkeypatch.setenv('NVIDIA_API_KEY','SECRET-123-TEST')
    seen=[]
    def transport(req,timeout):
        seen.append((req.full_url,timeout,dict(req.header_items()),json.loads(req.data)))
        class Resp:
            def __enter__(self):return io.BytesIO(json.dumps({'choices':[{'message':{'role':'assistant','content':'ok'}}]}).encode())
            def __exit__(self,*args):pass
        return Resp()
    model=agent_v03.NVIDIAClient(key='SECRET-123-TEST',model='nvidia/test-model',transport=transport)
    assert model.complete([{'role':'user','content':'hello'}])['content']=='ok'
    assert seen[0][0]=='https://integrate.api.nvidia.com/v1/chat/completions'
    assert seen[0][3]['model']=='nvidia/test-model'
    assert 'SECRET-123-TEST' not in agent_v03.scrub('SECRET-123-TEST')
    def down(*args,**kw):raise urllib.error.URLError('Bad network')
    with pytest.raises(agent_v03.ProviderError) as er:agent_v03.NVIDIAClient(key='SECRET-123-TEST',model='nvidia/test-model',transport=down).complete([{'role':'user','content':'hi'}])
    assert 'SECRET-123-TEST' not in str(er.value)


def test_zetaris_tenant_query_contract_with_mock_transport():
    captured=[]
    def transport(req,timeout):
        captured.append((req.full_url,timeout,json.loads(req.data),dict(req.header_items())))
        class Resp:
            def __enter__(self):return io.BytesIO(json.dumps({'rows':[{'lot':'MOCK'}]}).encode())
            def __exit__(self,*args):pass
        return Resp()
    model=zetaris.ZetarisClient(url='https://tenant.example',token='TEST-SECRET',path='/api/tenant/queries',transport=transport)
    result=model.query('RecallSource.notice',page_limit=4)
    assert result['mode']=='LIVE_TENANT_RESPONSE' # Fake transport only in THIS test.
    assert captured[0][2]=={'select':'SELECT * FROM RecallSource.notice','pageLimit':4}
    assert captured[0][1]==12
    assert captured[0][0]=='https://tenant.example/api/tenant/queries'
    for bad in ('sqlite_master','Table;DROP TABLE x','x..bad'):
        with pytest.raises(zetaris.ZetarisError):model.query(bad)
    with pytest.raises(zetaris.ZetarisError):model.query('RecallSource.notice',page_limit=101)
    assert client.get('/api/zetaris/status').json()['live_query_verified'] is False


def test_zetaris_unconfigured_route_is_fail_closed(isolated,monkeypatch):
    for key in ('ZETARIS_URL','ZETARIS_ID_TOKEN','ZETARIS_QUERY_PATH'):
        monkeypatch.delenv(key,raising=False)
    r=client.post('/api/zetaris/test-query')
    assert r.status_code==503 and ('token' in r.text.lower() or 'mapping' in r.text.lower())
    assert 'TEST-SECRET' not in r.text


def test_all_languages_accepted_source_text_not_rewritten(isolated):
    for loc in agent_v03.SUPPORTED_LOCALES:
        response=client.post('/api/agent/chat',json={'message':'Check evidence','language':loc})
        assert response.status_code==200
        assert response.json()['language']==loc
        assert response.json()['language_note'].startswith('Evidence')
