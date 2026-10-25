"""Test harness: real local login + CSRF, no production bypass."""
import os
from fastapi.testclient import TestClient

TEST_QA_PASSWORD='V04_test_only_password_very_long_2026'
TEST_ANALYST_PASSWORD='V04_analyst_test_only_password_2026'
os.environ.setdefault('FOODRECALL_BOOTSTRAP_PASSWORD',TEST_QA_PASSWORD)
os.environ.setdefault('FOODRECALL_ANALYST_PASSWORD',TEST_ANALYST_PASSWORD)

class AuthClient(TestClient):
    def __init__(self,app,role='qa_manager',**kwargs):
        super().__init__(app,**kwargs)
        self._role=role
        self._csrf=None
        self._marker=None

    def signin(self):
        from backend import app as api
        target=(api.DB_PATH,self._role)
        if target==self._marker and self._csrf:return
        username='qa@local.foodrecall' if self._role=='qa_manager' else 'analyst@local.foodrecall'
        password=TEST_QA_PASSWORD if self._role=='qa_manager' else TEST_ANALYST_PASSWORD
        r=super().post('/api/auth/login',json={'username':username,'password':password})
        assert r.status_code==200,r.text
        self._csrf=r.json()['csrf_token'];self._marker=target

    def post(self,url,*args,**kwargs):
        if url!='/api/auth/login':
            self.signin()
            headers=dict(kwargs.pop('headers',{}) or {})
            headers['X-CSRF-Token']=self._csrf
            kwargs['headers']=headers
        return super().post(url,*args,**kwargs)
