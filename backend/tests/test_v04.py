"""V0.4 policy tests: all endpoints through real FastAPI, real SQLite, real PBKDF2 login.
No external provider claims. Fake demo-role headers NEVER authorize writes.
"""
import os
from fastapi.testclient import TestClient
import pytest
from backend import app as api
from backend.tests.auth_support import TEST_QA_PASSWORD, TEST_ANALYST_PASSWORD

@pytest.fixture
def work(tmp_path,monkeypatch):
    monkeypatch.setattr(api,'DB_PATH',str(tmp_path/'v04.sqlite'))
    api.initialize()
    return TestClient(api.app)

def login(client,role='qa_manager'):
    who='qa@local.foodrecall' if role=='qa_manager' else 'analyst@local.foodrecall'
    password=TEST_QA_PASSWORD if role=='qa_manager' else TEST_ANALYST_PASSWORD
    r=client.post('/api/auth/login',json={'username':who,'password':password})
    assert r.status_code==200,r.text
    return {'X-CSRF-Token':r.json()['csrf_token']}

def test_no_session_and_fake_role_denied(work):
    assert work.post('/api/cases/DEMO-001/proposals',headers={'X-Demo-Role':'qa_manager'}).status_code==401
    assert work.post('/api/demo/reset',json={'confirm':'RESET_DEMO'}).status_code==401
    assert work.get('/api/auth/me').status_code==401

def test_login_logout_sessions_and_csrf(work):
    assert work.post('/api/auth/login',json={'username':'qa@local.foodrecall','password':'bad'}).status_code==401
    headers=login(work)
    assert work.get('/api/auth/me').json()['user']['role']=='qa_manager'
    assert work.post('/api/cases/DEMO-001/proposals').status_code==403
    assert work.post('/api/cases/DEMO-001/proposals',headers={'X-CSRF-Token':'forged'}).status_code==403
    assert work.post('/api/cases/DEMO-001/proposals',headers=headers).status_code==200
    assert work.post('/api/auth/logout',headers=headers).status_code==200
    assert work.post('/api/cases/DEMO-001/proposals',headers=headers).status_code==401

def test_analyst_cannot_approve_even_with_forged_header(work):
    qa=login(work)
    p=work.post('/api/cases/DEMO-001/proposals',headers=qa).json()['id']
    analyst=TestClient(api.app)
    ah=login(analyst,'analyst')
    headers={**ah,'X-Demo-Role':'qa_manager'}
    assert analyst.post(f'/api/proposals/{p}/approve',json={'reviewer':'Spoofed'},headers=headers).status_code==403
    assert analyst.post('/api/demo/reset',json={'confirm':'RESET_DEMO'},headers=ah).status_code==403
    assert analyst.post('/api/cases/DEMO-001/proposals',headers=ah).status_code==200
    assert work.post(f'/api/proposals/{p}/approve',json={'reviewer':'irrelevant claimed name'},headers=qa).status_code==200
    assert work.get('/api/cases/DEMO-001/proposals').json()[1]['approved_by']=='qa@local.foodrecall'

def test_approval_and_execution_verified_with_identity(work):
    h=login(work)
    proposal=work.post('/api/cases/DEMO-001/proposals',headers=h).json();pid=proposal['id']
    assert proposal['critical_dependencies_hash']
    assert work.post(f'/api/proposals/{pid}/approve',json={'reviewer':'user forged'},headers=h).json()['reviewer']=='qa@local.foodrecall'
    response=work.post(f'/api/proposals/{pid}/execute',headers=h)
    assert response.status_code==200 and response.json()['status']=='verified'
    assert work.post(f'/api/proposals/{pid}/execute',headers=h).json()['idempotent_replay'] is True
    assert work.get('/api/proposals/'+str(pid)+'/decision-diff').json()['current'] is True

def test_unrelated_evidence_does_not_invalidate_approval(work):
    h=login(work);pid=work.post('/api/cases/DEMO-001/proposals',headers=h).json()['id']
    with api.db() as c:
        c.execute("INSERT INTO evidence(id,case_id,kind,title,detail,version,provenance) VALUES ('E-99','DEMO-001','analyst_note','Irrelevant','Unrelated note changed',1,'Training')")
    d=work.get(f'/api/proposals/{pid}/decision-diff').json()
    assert d['current'] is True and d['changes']==[]
    assert work.post(f'/api/proposals/{pid}/approve',json={'reviewer':'Real'},headers=h).status_code==200

def test_material_supplier_update_blocks_stale_approval_and_shows_diff(work):
    h=login(work);pid=work.post('/api/cases/DEMO-001/proposals',headers=h).json()['id']
    assert work.post(f'/api/proposals/{pid}/approve',json={'reviewer':'QA'},headers=h).status_code==200
    assert work.post('/api/cases/DEMO-001/simulate-revision',json={'confirm':'SIMULATE'},headers=h).status_code==200
    d=work.get(f'/api/proposals/{pid}/decision-diff').json()
    assert not d['current'] and {x['id'] for x in d['changes']}=={'RB-073','E-03'}
    out=work.post(f'/api/proposals/{pid}/execute',headers=h)
    assert out.status_code==409
    assert all(x['status']=='available' for x in work.get('/api/cases/DEMO-001/investigation').json()['lots'])

def test_critical_evidence_revision_even_same_lots_invalidates(work):
    h=login(work);pid=work.post('/api/cases/DEMO-001/proposals',headers=h).json()['id']
    with api.db() as c:
        c.execute("UPDATE evidence SET version=version+1,detail='Material correction' WHERE id='E-01'")
    d=work.get(f'/api/proposals/{pid}/decision-diff').json()
    assert not d['current'] and d['changes'][0]['id']=='E-01'
    assert work.post(f'/api/proposals/{pid}/approve',json={'reviewer':'QA'},headers=h).status_code==409

def test_partial_legacy_proposal_without_dependency_fails_closed(work):
    h=login(work)
    pid=work.post('/api/cases/DEMO-001/proposals',headers=h).json()['id']
    with api.db() as c:c.execute('DELETE FROM proposal_dependencies WHERE proposal_id=?',(pid,))
    d=work.get(f'/api/proposals/{pid}/decision-diff').json()
    assert not d['current'] and d['legacy_without_dependencies'] is True
    assert work.post(f'/api/proposals/{pid}/approve',json={'reviewer':'QA'},headers=h).status_code==409

def test_qa_can_add_auditor_with_zero_write_authority(work):
    h=login(work)
    created=work.post('/api/auth/users',json={'username':'audit@example.test','password':'Secure_Auditor_2026_Long','role':'auditor'},headers=h)
    assert created.status_code==200
    visitor=TestClient(api.app)
    r=visitor.post('/api/auth/login',json={'username':'audit@example.test','password':'Secure_Auditor_2026_Long'})
    assert r.status_code==200
    assert visitor.get('/api/audit').status_code==200
    assert visitor.post('/api/cases/DEMO-001/proposals',headers={'X-CSRF-Token':r.json()['csrf_token']}).status_code==403

def test_remote_mutations_blocked_even_if_cookie_copied(work):
    h=login(work)
    cookie=work.cookies.get('foodrecall_session')
    remote=TestClient(api.app,client=('203.0.113.8',9999))
    remote.cookies.set('foodrecall_session',cookie)
    assert remote.post('/api/cases/DEMO-001/proposals',headers=h).status_code==403
