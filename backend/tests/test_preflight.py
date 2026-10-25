from scripts.preflight import build_report


def test_preflight_never_equates_keys_with_verified(monkeypatch):
    for k in ('NVIDIA_API_KEY','NVIDIA_MODEL','ZETARIS_URL','ZETARIS_ID_TOKEN',
              'ZETARIS_QUERY_PATH','ZETARIS_RECALL_TABLE','ZETARIS_SHIPMENT_TABLE'):
        monkeypatch.setenv(k,'secret_test_value_do_not_publish')
    report=build_report(live=False)
    assert report['checks']['nvidia']['configuration']=='PRESENT_NOT_VERIFIED'
    assert report['checks']['zetaris']['configuration']=='PRESENT_NOT_VERIFIED'
    assert report['live_tests']=={}
    assert report['release_verdict']=='NOT_PRODUCTION_READY'
    assert 'secret_test_value_do_not_publish' not in str(report)


def test_offline_preflight_never_makes_live_claim(monkeypatch):
    monkeypatch.delenv('NVIDIA_API_KEY',raising=False)
    report=build_report()
    assert report['checks']['nvidia']['configuration']=='MISSING'
    assert report['checks']['external_data_linkage']['status']=='NOT_VERIFIED'
