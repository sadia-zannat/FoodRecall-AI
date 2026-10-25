"""Checks defense in depth; no false claim of production penetration testing."""
from fastapi.testclient import TestClient
from backend import app

client=TestClient(app.app)

def test_html_security_headers():
    r=client.get('/')
    assert r.status_code==200
    assert r.headers['x-frame-options']=='DENY'
    assert r.headers['x-content-type-options']=='nosniff'
    csp=r.headers['content-security-policy']
    assert "script-src 'self'" in csp
    assert "object-src 'none'" in csp


def test_identity_requests_do_not_cache():
    assert client.get('/api/auth/me').headers['cache-control']=='no-store'


def test_unsupported_remote_host_remains_read_only():
    external=TestClient(app.app,client=('198.51.100.14',9999))
    assert external.post('/api/agent/chat',json={'message':'please investigate'}).status_code==403
    assert external.get('/api/health').status_code==200
    assert external.get('/api/health').json()['live_production'] is False
