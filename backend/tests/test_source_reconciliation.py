import pytest
from backend.source_reconciliation import reconcile_sources
from backend.sponsor_evidence import project_sources


def test_exact_identifier_candidate_not_verified():
    r=reconcile_sources([{'gtin':'00012345','lot_number':'L-1','product_description':'abc'}],
                        [{'gtin':'00012345','lot_id':'L-1','quantity':42}])
    assert r['candidate_count']==1
    assert r['candidate_preview'][0]['status']=='UNVERIFIED_JOIN_CANDIDATE'
    assert r['verified_inventory_links']==[] and r['writes_performed']==0


def test_name_similarity_cannot_link():
    result=reconcile_sources([{'lot_id':'L1','product_description':'Apple'}],
                             [{'lot_id':'L1','product_description':'Apple'}])
    assert result['candidate_count']==0


def test_exact_lot_different_gtin_is_conflict():
    result=reconcile_sources([{'lot_id':'L1','gtin':'1111'}],
                             [{'lot_id':'L1','gtin':'2222'}])
    assert result['candidate_count']==0
    assert result['conflict_count']==1


def test_conflicting_identifier_format_fail_closed():
    for bad in [None,{},[],True,'invalid space']:
        assert reconcile_sources([{'gtin':'1234','lot_id':bad}],
                                 [{'gtin':'1234','lot_id':bad}])['candidate_count']==0


def test_leading_zeroes_preserved():
    r=reconcile_sources([{'gtin':'0001234','lot_id':'X'}], [{'gtin':'1234','lot_id':'X'}])
    assert r['candidate_count']==0 and r['conflict_count']==1


def test_candidate_preview_bounded():
    rows=[{'lot_id':f'L{i}','gtin':'1234'} for i in range(40)]
    r=reconcile_sources(rows,rows)
    assert r['candidate_count']==40 and len(r['candidate_preview'])==10
    assert r['preview_truncated']


def test_unrecognized_sources_undecidable():
    d={'recall':{'mode':'LIVE_TENANT_RESPONSE','query':'SELECT ...','response':{'strange':[]}},
       'shipment':{'mode':'LIVE_TENANT_RESPONSE','query':'SELECT ...','response':[]}}
    r=project_sources(d)
    assert r['reconciliation']['status']=='UNRESOLVED_SOURCE_SCHEMA'
    assert r['verified_links']==[]


def test_project_sources_success_with_candidate():
    query=lambda rows:{'mode':'LIVE_TENANT_RESPONSE','query':'SELECT ...','response':{'results':rows}}
    d={'recall':query([{'gtin':'012345','lot_id':'A'}]),
       'shipment':query([{'gtin':'012345','lot_id':'A'}])}
    r=project_sources(d)
    assert r['reconciliation']['candidate_count']==1
    assert r['verified_links']==[]


def test_invalid_reconciliation_payload():
    with pytest.raises(ValueError):reconcile_sources(None,[])
