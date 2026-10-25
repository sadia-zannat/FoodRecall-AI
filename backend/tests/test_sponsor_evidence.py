"""Mocked provider payload contracts. These tests DO NOT establish live sponsor access."""
import pytest
from backend.sponsor_evidence import project_query, project_sources
from backend import agent_v03


def payload(rows, wrapper='results'):
    return {'mode':'LIVE_TENANT_RESPONSE','query':'SELECT * FROM training.recall_records',
            'response':{wrapper:rows}}


def test_real_rows_projected_without_auto_inventory_matching():
    sources=project_sources({'recall':payload([{'recall_number':'R-20','product_description':'Test'}]),
                             'shipment':payload([{'shipment_id':'S-07','lot_id':'X-123'}])})
    assert sources['sources']['recall']['row_count']==1
    assert sources['sources']['shipment']['identifiers'][0]['lot_id']=='X-123'
    assert sources['verified_links']==[]
    assert not sources['sources']['shipment']['verified_inventory_linkage']


def test_unparseable_payload_is_not_presented_as_verified_records():
    out=project_query(payload([],wrapper='unrecognized'),'shipment')
    assert not out['response_parsed'] and out['row_count'] is None


@pytest.mark.parametrize('bad', [{'error':'Invalid token'}, {'errors':['not authorized']}, {'success':False,'results':[]}])
def test_embedded_provider_errors_are_rejected(bad):
    with pytest.raises(ValueError):project_query({'mode':'LIVE_TENANT_RESPONSE','query':'SELECT 1','response':bad},'recall')


def test_agent_answer_retains_sponsor_row_count_and_citations():
    report=agent_v03.compose_answer('inspect',{
       'zetaris_sources':project_sources({'recall':payload([{'recall_number':'R-20'}]),
                                          'shipment':payload([{'shipment_id':'S-07'},{'shipment_id':'S-08'}])})
    },'DEMO-001')
    assert 'recall=1 row(s)' in report['answer']
    assert 'shipment=2 row(s)' in report['answer']
    assert {'ZETARIS:RECALL','ZETARIS:SHIPMENT'}=={e['id'] for e in report['citations']}
    assert report['write_actions_taken']==0
