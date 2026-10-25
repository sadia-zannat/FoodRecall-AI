"""Regression: a remote guest could read all case/audit/source records in V0.5."""
from fastapi.testclient import TestClient
from backend.app import app


def test_remote_private_gets_blocked():
    with TestClient(app,client=('198.51.100.17',443)) as c:
        for path in ('/api/cases','/api/cases/DEMO-001/investigation',
                     '/api/audit','/api/agent/runs','/api/fda/records',
                     '/api/traceability/graph','/api/agent/status'):
            assert c.get(path).status_code==403,path
        assert c.get('/api/health').status_code==200
        assert c.post('/api/auth/login',json={'username':'nobody@local.test','password':'guess'}).status_code==403
