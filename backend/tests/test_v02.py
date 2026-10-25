"""V0.2 deterministic end-to-end data-layer and failure-contract tests.

The FDA results in these tests are synthetic fixtures. No test claims live FDA access.
"""
import io
import json
import os
import sqlite3
import urllib.error
from pathlib import Path
from backend.tests.auth_support import AuthClient as TestClient
import pytest
from backend import fda,traceability
from backend.app import app

client=TestClient(app)

def report(n='F-TRAIN-0001', description='Test product'):
    return {'recall_number':n,'event_id':'EVENT-TEST','product_description':description,
            'recalling_firm':'Synthetic Test Only','code_info':'Lot unstructured',
            'reason_for_recall':'Mock laboratory testing','classification':'Class II',
            'report_date':'20260928','status':'Ongoing', 'extra_field_preserved':'test'}


def fake_urlopen(payload):
    def fetch(req,timeout):
        assert timeout==12
        assert req.full_url.startswith('https://api.fda.gov/food/enforcement.json?')
        class Response:
            def __enter__(self):return io.BytesIO(json.dumps(payload).encode())
            def __exit__(self,*a):pass
        return Response()
    return fetch

@pytest.fixture
def isolated_fda_db(tmp_path,monkeypatch):
    path=tmp_path/'test_fda.sqlite'
    def connect():
        from contextlib import contextmanager
        @contextmanager
        def ctx():
            with sqlite3.connect(path,isolation_level=None) as conn:
                conn.row_factory=sqlite3.Row
                yield conn
        return ctx()
    with connect() as c:fda.init_tables(c)
    return connect

def test_fda_mock_request_includes_pagination_and_validated_search(monkeypatch):
    monkeypatch.setattr(fda.urllib.request,'urlopen',fake_urlopen({'results':[report()]}))
    assert fda.fetch_page(1,0)[0]['recall_number']=='F-TRAIN-0001'
    assert 'skip=50' in fda.build_url(25,50)
    assert 'search=product_description' in fda.build_url(25,0,'moringa')
    with pytest.raises(fda.FDAError):fda.build_url(25,0,'unsafe" OR recall_number:*')
    with pytest.raises(fda.FDAError):fda.build_url(101,0)

def test_fda_sync_create_dedupe_revise_and_raw_hash(isolated_fda_db,monkeypatch):
    connect=isolated_fda_db
    staged=[report(),report('F-TRAIN-0002','Another mock product')]
    monkeypatch.setattr(fda,'fetch_page',lambda *args,**kwargs:staged)
    first=fda.sync(connect,pages=1,per_page=2)
    assert first['inserted']==2 and first['source']=='live openFDA API'
    # The wording denotes a successful response from the mocked transport IN THIS TEST ONLY.
    with connect() as c:
        listing=fda.list_records(c,search='Another')
        assert listing['total']==1
        r=fda.get_record(c,'F-TRAIN-0001')
        assert r['normalized']['lot_parse_status']=='UNVERIFIED_FREE_TEXT'
        assert r['normalized']['inventory_mapping']=='NONE'
        assert r['raw']['extra_field_preserved']=='test'
        assert r['provenance']['content_sha256']==fda.digest(report())
        assert 'api_key' not in r['provenance']['source_uri']
    second=fda.sync(connect,pages=1,per_page=2)
    assert second['unchanged']==2 and second['inserted']==0
    staged[0]=report(description='Updated from mock FDA transport')
    changed=fda.sync(connect,pages=1,per_page=2)
    assert changed['updated']==1 and changed['unchanged']==1
    with connect() as c:
        updated=fda.get_record(c,'F-TRAIN-0001')
        assert updated['provenance']['version']==2
        assert len(updated['versions'])==2
        assert c.execute('SELECT count(*) FROM fda_record_versions').fetchone()[0]==3

def test_fda_rollback_on_corrupt_second_record(isolated_fda_db,monkeypatch):
    monkeypatch.setattr(fda,'fetch_page',lambda *args,**kwargs:[report(),{'product_description':'missing ID'}])
    with pytest.raises(fda.FDAError) as exc:fda.sync(isolated_fda_db)
    assert exc.value.code=='INVALID_FDA_RECORD'
    with isolated_fda_db() as c:
        assert fda.list_records(c)['total']==0
        assert c.execute('SELECT status FROM fda_sync_runs').fetchone()[0]=='failed'

def test_fda_timeout_and_http_429_are_bounded_and_no_secrets(monkeypatch):
    times=[]
    monkeypatch.setattr(fda.urllib.request,'urlopen',lambda *a,**kw: (_ for _ in ()).throw(urllib.error.URLError('offline')))
    with pytest.raises(fda.FDAError) as ex:fda.fetch_page(10,0,sleep=lambda n:times.append(n))
    assert ex.value.code=='FDA_UNREACHABLE' and times==[1,2]
    times=[]
    def limit(req,timeout):raise urllib.error.HTTPError(req.full_url,429,'rate limit',{},None)
    monkeypatch.setattr(fda.urllib.request,'urlopen',limit)
    with pytest.raises(fda.FDAError) as ex:fda.fetch_page(10,0,sleep=lambda n:times.append(n))
    assert ex.value.code=='FDA_UNAVAILABLE' and len(times)==2
    monkeypatch.setenv('OPENFDA_API_KEY','SECRET_CANNOT_SHOW')
    assert 'SECRET_CANNOT_SHOW' not in fda.public_record_uri('F-TEST')
    assert 'SECRET_CANNOT_SHOW' not in str(ex.value)

def test_fda_404_means_no_results(monkeypatch):
    def missing(req,timeout): raise urllib.error.HTTPError(req.full_url,404,'Not found',{},None)
    monkeypatch.setattr(fda.urllib.request,'urlopen',missing)
    assert fda.fetch_page(10,0)==[]

def test_fda_page_count_bounded_by_5(isolated_fda_db,monkeypatch):
    calls=[]
    def page(n,skip,search):
        calls.append(skip)
        return [report(f'F-TRAIN-{skip:04d}')]
    monkeypatch.setattr(fda,'fetch_page',page)
    got=fda.sync(isolated_fda_db,pages=5,per_page=1)
    assert calls==[0,1,2,3,4] and got['inserted']==5
    with pytest.raises(fda.FDAError):fda.sync(isolated_fda_db,pages=6)

def test_fda_api_empty_cache_and_invalid_inputs():
    assert client.get('/api/fda/records').status_code==200
    assert client.get('/api/fda/records?limit=200').status_code==422
    assert client.get('/api/fda/records/not-exists').status_code==404
    assert client.post('/api/fda/sync',json={'per_page':500}).status_code==422
    assert client.get('/api/fda/sync-status').status_code==200

def test_fda_api_mock_end_to_end_with_local_sqlite(monkeypatch):
    monkeypatch.setattr(fda,'fetch_page',lambda *a,**k:[report('FDA-MOCK-V02')])
    response=client.post('/api/fda/sync',json={'pages':1,'per_page':5})
    assert response.status_code==200
    detail=client.get('/api/fda/records/FDA-MOCK-V02')
    assert detail.status_code==200
    assert detail.json()['raw']['recall_number']=='FDA-MOCK-V02'
    preview=client.get('/api/fda/records/FDA-MOCK-V02/trace-preview')
    assert preview.status_code==200 and preview.json()['write_actions_taken']==0
    assert preview.json()['authorization_status']=='NO_VERIFIED_INVENTORY_LINK'
    assert len(detail.json()['versions'])>=1
    assert client.get('/api/fda/records?search=FDA-MOCK').json()['total']>=1
    # Cleanup only the synthetic mock inserted in this test, never erase real live data.
    from backend.app import db
    with db() as c:
        c.execute('DELETE FROM fda_record_versions WHERE recall_number=?',('FDA-MOCK-V02',))
        c.execute('DELETE FROM fda_records WHERE recall_number=?',('FDA-MOCK-V02',))

def test_epcis_training_graph_is_synthetic_and_linkless():
    response=client.get('/api/traceability/graph')
    assert response.status_code==200
    graph=response.json()
    assert graph['origin']=='SYNTHETIC_TRAINING' and not graph['linked_fda_recall_numbers']
    assert graph['event_count']==7 and len(graph['edges'])>=7
    for item in client.get('/api/traceability/events').json()['events']:
        assert traceability.validate_event(item)==[]
    assert client.post('/api/traceability/validate',json={'event':{'type':'ObjectEvent'}}).json()['valid'] is False

def test_remote_clients_denied_any_writes_but_allowed_reads():
    from fastapi.testclient import TestClient as RawClient
    remote=RawClient(app,client=('203.0.113.123',12345))
    assert remote.post('/api/demo/reset',json={'confirm':'RESET_DEMO'}).status_code==403
    assert remote.post('/api/fda/sync',json={}).status_code==403
    assert remote.post('/api/cases/DEMO-001/proposals').status_code==403
    assert remote.get('/api/health').status_code==200
