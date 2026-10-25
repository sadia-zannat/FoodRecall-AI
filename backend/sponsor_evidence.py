"""Narrow evidence projection of *actual* Zetaris query response shapes.

Never equates cross-source product names with verified lot relationships. No synthetic
rows are substituted after an upstream failure. Projection exposes only a small
allowlist of identifiers for local investigation; all full results stay in the
Zetaris provider response, not saved to persistent agent logs.
"""
from __future__ import annotations
import hashlib
import json

DISPLAY_FIELDS=('recall_number','event_id','lot_id','lot_number','shipment_id','gtin','product_code','product_description','status')


def _rows(result:dict):
    """Accept only recognized record shapes after transport/application checks."""
    raw=result.get('response')
    candidates=[raw]
    if isinstance(raw,dict):
        candidates.extend(raw.get(k) for k in ('rows','results','data','records'))
    for obj in candidates:
        if isinstance(obj,list) and all(isinstance(x,dict) for x in obj):
            return obj
        if isinstance(obj,dict):
            for key in ('rows','results','data','records'):
                v=obj.get(key)
                if isinstance(v,list) and all(isinstance(x,dict) for x in v):return v
    return None


def project_query(result:dict, label:str)->dict:
    if not isinstance(result,dict) or result.get('mode')!='LIVE_TENANT_RESPONSE':
        raise ValueError('No verified Zetaris transport response')
    raw=result.get('response')
    if isinstance(raw,dict) and (raw.get('success') is False or raw.get('error') or raw.get('errors')):
        raise ValueError('Zetaris returned an application-level query error')
    # A partial or unrecognized page is unresolved, never an empty result.
    records=_rows(result)
    query=str(result.get('query') or '')
    base={'source':f'ZETARIS:{label.upper()}','query_sha256':hashlib.sha256(query.encode()).hexdigest(),
          'query_executed':bool(query),'origin':'ZETARIS_LIVE_TENANT',
          'verified_inventory_linkage':False}
    if records is None:
        return {**base,'row_count':None,'response_parsed':False,'identifiers':[],
                'warning':'Tenant response shape not recognized; rows NOT verified'}
    ids=[]
    for record in records[:10]:
        safe={k:str(record[k])[:90] for k in DISPLAY_FIELDS if record.get(k) is not None and isinstance(record[k],(str,int,float))}
        if safe:ids.append(safe)
    return {**base,'row_count':len(records),'response_parsed':True,'identifiers':ids,
            'warning':'Returned page rows are not independently linked to inventory; pagination may be incomplete'}


def project_sources(data:dict)->dict:
    if not isinstance(data,dict) or not all(k in data for k in ('recall','shipment')):
        raise ValueError('Missing one of the two required Zetaris sources')
    sources={name:project_query(data[name],name) for name in ('recall','shipment')}
    from backend.source_reconciliation import reconcile_sources
    if all(s['response_parsed'] for s in sources.values()):
        # Cross-source analysis uses strictly parsed rows from actual responses.
        # It does not create verified FDA-to-inventory links.
        reconciliation=reconcile_sources(_rows(data['recall']),_rows(data['shipment']))
    else:
        reconciliation={'status':'UNRESOLVED_SOURCE_SCHEMA','candidate_count':0,
                        'candidate_preview':[],'conflict_count':0,'conflict_preview':[],
                        'verified_inventory_links':[],'writes_performed':0}
    return {'origin':'ZETARIS_LIVE_TENANT','sources':sources,
            'reconciliation':reconciliation,'verified_links':[], 'writes_performed':0}
