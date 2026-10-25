"""Contract tests: fake JDBC only. NOT proof that user's real Zetaris is live."""
import pytest
from backend import zetaris
from backend.zetaris_jdbc import ZetarisJDBCClient
from backend.sponsor_evidence import project_sources


class Cursor:
    def __init__(self, owner): self.owner=owner; self.description=[('lot_id',),('quantity',)]
    def execute(self, sql): self.owner.calls.append(sql)
    def fetchall(self): return [('RB-071',120)]
    def close(self): self.owner.cursor_closed=True


class Connection:
    def __init__(self):self.calls=[];self.cursor_closed=False;self.closed=False
    def cursor(self):return Cursor(self)
    def close(self):self.closed=True


def mock_client(connection, **kwargs):
    def connect(driver, url, credentials, jar):
        assert driver=='com.zetaris.lightning.jdbc.LightningDriver'
        assert credentials==['test_user','test_password']
        assert url=='jdbc:zetaris:lightning@localhost:10000'
        return connection
    return ZetarisJDBCClient(user='test_user', password='test_password', jar='fake.jar', connect=connect, **kwargs)


def test_select1_and_bounded_read_only_query():
    conn=Connection();client=mock_client(conn)
    assert client.ping()['status']=='LIVE_SELECT1_OBSERVED'
    assert conn.calls==['SELECT 1']
    assert conn.closed and conn.cursor_closed
    conn2=Connection();client=mock_client(conn2)
    out=client.query('training.recall_records',columns=('lot_id','quantity'),page_limit=3)
    assert conn2.calls==['SELECT lot_id, quantity FROM training.recall_records LIMIT 3']
    assert out['transport']=='zetaris_local_jdbc'
    assert project_sources({'recall':out,'shipment':out})['sources']['recall']['row_count']==1
    assert out['response']['rows']==[{'lot_id':'RB-071','quantity':120}]


@pytest.mark.parametrize('table',["training.recall;DROP TABLE x", 'unqualified', 'x..bad'])
def test_fail_closed_table_identifiers(table):
    conn=Connection()
    with pytest.raises(zetaris.ZetarisError):mock_client(conn).query(table)
    assert conn.calls==[]


def test_invalid_remote_jdbc_and_credentials_are_not_exposed():
    with pytest.raises(zetaris.ZetarisError):
        ZetarisJDBCClient(url='jdbc:zetaris:lightning@external.example:10000',user='test',password='PRIVATE',jar='a.jar')
    def broken(*args):raise RuntimeError('PRIVATE password leaked by JDBC')
    model=ZetarisJDBCClient(user='test_user',password='PRIVATE',jar='test.jar',connect=broken)
    with pytest.raises(zetaris.ZetarisError) as error:model.ping()
    assert 'PRIVATE' not in str(error.value)


def test_mode_selects_local_with_no_cloud_token(monkeypatch):
    monkeypatch.setenv('ZETARIS_MODE','jdbc')
    monkeypatch.setenv('ZETARIS_JDBC_USER','qa@zetaris.com')
    monkeypatch.setenv('ZETARIS_JDBC_PASSWORD','PRIVATE')
    monkeypatch.setenv('ZETARIS_JDBC_JAR','fake.jar')
    for key in ('ZETARIS_URL','ZETARIS_ID_TOKEN','ZETARIS_QUERY_PATH'):
        monkeypatch.delenv(key,raising=False)
    assert zetaris.configured()
    assert isinstance(zetaris.active_client(),ZetarisJDBCClient)
    monkeypatch.setenv('ZETARIS_MODE','broken')
    with pytest.raises(zetaris.ZetarisError):zetaris.active_client()


def test_real_data_mappings_never_invented(monkeypatch):
    conn=Connection()
    client=mock_client(conn)
    for key in ('ZETARIS_RECALL_TABLE','ZETARIS_SHIPMENT_TABLE'):
        monkeypatch.delenv(key,raising=False)
    with pytest.raises(zetaris.ZetarisError):client.read_approved_sources()
    assert conn.calls==[]
