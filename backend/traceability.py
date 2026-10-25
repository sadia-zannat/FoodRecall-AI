"""Bounded EPCIS 2.0-shaped staging events and queryable provenance graph.

GS1-compatible *data representation* only, not a certified EPCIS repository.
All provided logistics events are explicitly synthetic and do not map to FDA items.
"""
import hashlib
import json
from pathlib import Path
from datetime import datetime

FIXTURE=Path(__file__).resolve().parent.parent/'data'/'synthetic_epcis_events.json'
TYPES={'ObjectEvent','AggregationEvent','TransformationEvent','TransactionEvent','AssociationEvent'}

def validate_event(value):
    problems=[]
    if not isinstance(value,dict): return ['Event must be a JSON object']
    if value.get('type') not in TYPES:problems.append('Unknown EPCIS event type')
    for k in ('eventID','eventTime','eventTimeZoneOffset','bizStep'):
        if not isinstance(value.get(k),str) or not value[k].strip(): problems.append(f'Missing {k}')
    try:
        datetime.fromisoformat(value.get('eventTime','').replace('Z','+00:00'))
    except ValueError: problems.append('Invalid eventTime')
    if value.get('type')=='ObjectEvent':
        if value.get('action') not in ('ADD','OBSERVE','DELETE'):problems.append('Invalid ObjectEvent action')
        items=value.get('quantityList')
        if not isinstance(items,list) or not items:problems.append('ObjectEvent needs quantityList')
        else:
            for item in items:
                if not isinstance(item,dict) or not str(item.get('epcClass','')).startswith('urn:epc:class:lgtin:') or type(item.get('quantity')) not in (int,float) or item['quantity']<=0:
                    problems.append('quantityList needs a LGTIN epcClass and positive quantity')
    if not isinstance(value.get('bizLocation'),dict) or not str(value['bizLocation'].get('id','')).startswith('urn:epc:id:sgln:'):
        problems.append('Missing GS1 SGLN business location')
    return problems

def load_events():
    data=json.loads(FIXTURE.read_text('utf-8'))
    assert data.get('origin')=='SYNTHETIC_TRAINING'
    events=data['events']; ids=set()
    for e in events:
        errors=validate_event(e)
        if errors:raise ValueError('Invalid bundled EPCIS training event: '+', '.join(errors))
        if e['eventID'] in ids:raise ValueError('Duplicate eventID')
        ids.add(e['eventID'])
    return {'origin':data['origin'],'standards_note':data.get('standards_note'),'events':events,
            'fixture_sha256':hashlib.sha256(FIXTURE.read_bytes()).hexdigest()}

def graph():
    data=load_events(); nodes={}; edges=[]
    def node(id,kind,label):nodes[id]={'id':id,'kind':kind,'label':label,'origin':'SYNTHETIC_TRAINING'}
    for e in data['events']:
        eid=e['eventID']; loc=e['bizLocation']['id'];
        node(eid,'event',e['bizStep'].split('/')[-1]+' @ '+e['eventTime'][:10]);node(loc,'location',loc.split(':')[-1])
        edges.append({'from':eid,'to':loc,'type':'observed_at','eventID':eid})
        for item in e.get('quantityList',[]):
            lot=item['epcClass'];node(lot,'lot',lot.split('.')[-1])
            edges.append({'from':lot,'to':eid,'type':'observed_in','quantity':item['quantity'],'eventID':eid})
        for k,direction in [('sourceList','source'),('destinationList','destination')]:
            for entry in e.get(k,[]):
                if entry.get('type')!='urn:epcglobal:cbv:sdt:location':continue
                obj=entry['source' if k=='sourceList' else 'destination'];node(obj,'location',obj.split(':')[-1]);edges.append({'from':eid,'to':obj,'type':direction,'eventID':eid})
    return {'origin':'SYNTHETIC_TRAINING','nodes':list(nodes.values()),'edges':edges,'event_count':len(data['events']),
            'fixture_sha256':data['fixture_sha256'],'linked_fda_recall_numbers':[],
            'warning':'GS1 EPCIS-shaped training logistics ONLY; not real shipments or proof of FDA product/lot match.'}
