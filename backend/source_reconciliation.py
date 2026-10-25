"""Conservative, read-only cross-source candidate analysis.

Equal unverified identifiers across two independently queried sources are only
CANDIDATES. A business-authorized GS1/master-data mapping and physical inventory
readback are required to establish an operational link or authorize a stock hold.
No similarity score or LLM output can promote a candidate to a verified match.
"""
from __future__ import annotations
import re

LOT_FIELDS=('lot_id','lot_number')
MAX_CANDIDATES=10


def _token(value, max_length=90):
    if not isinstance(value,(str,int)) or isinstance(value,bool):return ''
    text=str(value).strip()
    if not text or len(text)>max_length or not re.fullmatch(r'[\w.\-\/]+',text,flags=re.ASCII):return ''
    return text


def _index(records):
    index={}
    by_lot={}
    for rec in records:
        if not isinstance(rec,dict):continue
        gtin=_token(rec.get('gtin'),18)
        lot=_token(rec.get('lot_id') or rec.get('lot_number'))
        if not lot:continue
        if gtin:
            index.setdefault((gtin,lot),0)
            index[(gtin,lot)]+=1
            by_lot.setdefault(lot,set()).add(gtin)
    return index,by_lot


def reconcile_sources(recall_rows,shipment_rows):
    """Only exact composite (GTIN, lot) equality; no fuzzy product joins."""
    if not isinstance(recall_rows,list) or not isinstance(shipment_rows,list):
        raise ValueError('Reconciliation requires parsed row arrays')
    recall,recall_lots=_index(recall_rows)
    shipment,shipment_lots=_index(shipment_rows)
    common=sorted(set(recall)&set(shipment))
    candidates=[{'gtin':gtin,'lot':lot,'status':'UNVERIFIED_JOIN_CANDIDATE',
                 'recall_rows':recall[(gtin,lot)],'shipment_rows':shipment[(gtin,lot)]}
                for gtin,lot in common[:MAX_CANDIDATES]]
    conflicts=[]
    for lot in sorted(set(recall_lots)&set(shipment_lots)):
        left=recall_lots[lot];right=shipment_lots[lot]
        if not (left & right):
            conflicts.append({'lot':lot,'kind':'CONFLICTING_GTIN_FOR_SAME_LOT',
                              'recall_gtins':sorted(left),'shipment_gtins':sorted(right)})
    return {'status':'CANDIDATES_NOT_VERIFIED',
            'candidate_count':len(common),'candidate_preview':candidates,
            'conflict_count':len(conflicts),'conflict_preview':conflicts[:MAX_CANDIDATES],
            'verified_inventory_links':[], 'writes_performed':0,
            'interpretation':'Exact identifiers across tenant queries suggest review candidates only. No business-master-data validation, FDA mapping, or physical lot authorization.',
            'preview_truncated':len(common)>MAX_CANDIDATES or len(conflicts)>MAX_CANDIDATES}
