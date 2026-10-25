"""openFDA food enforcement ingest, retaining raw provenance and revisions.

FDA food enforcement reports are historical weekly enforcement data, NOT live alerts
and NOT automatic evidence that any private inventory lot is affected.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

BASE = 'https://api.fda.gov/food/enforcement.json'
PUBLIC_INFO = 'https://open.fda.gov/apis/food/enforcement/'
FIELDS = ('recall_number','event_id','product_description','recalling_firm','reason_for_recall',
          'classification','code_info','more_code_info','report_date','recall_initiation_date',
          'status','distribution_pattern','product_quantity','voluntary_mandated')

class FDAError(Exception):
    def __init__(self, code: str, message: str, http_status: int = 503):
        super().__init__(message)
        self.code, self.http_status = code, http_status


def utc():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def canonical(obj: Any) -> str:
    return json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':'))


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode('utf-8')).hexdigest()


def init_tables(conn: sqlite3.Connection):
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS fda_records(
      recall_number TEXT PRIMARY KEY, normalized_json TEXT NOT NULL, raw_json TEXT NOT NULL,
      content_sha256 TEXT NOT NULL, version INTEGER NOT NULL, first_observed_at TEXT NOT NULL,
      last_observed_at TEXT NOT NULL, source_uri TEXT NOT NULL, source_system TEXT NOT NULL DEFAULT 'openFDA food enforcement');
    CREATE TABLE IF NOT EXISTS fda_record_versions(
      recall_number TEXT NOT NULL, version INTEGER NOT NULL, raw_json TEXT NOT NULL,
      normalized_json TEXT NOT NULL, content_sha256 TEXT NOT NULL, observed_at TEXT NOT NULL,
      source_uri TEXT NOT NULL, PRIMARY KEY(recall_number,version));
    CREATE TABLE IF NOT EXISTS fda_sync_runs(
      id INTEGER PRIMARY KEY AUTOINCREMENT, started_at TEXT NOT NULL, finished_at TEXT,
      status TEXT NOT NULL, fetched INTEGER NOT NULL DEFAULT 0, inserted INTEGER NOT NULL DEFAULT 0,
      updated INTEGER NOT NULL DEFAULT 0, unchanged INTEGER NOT NULL DEFAULT 0, detail TEXT NOT NULL DEFAULT '');
    CREATE INDEX IF NOT EXISTS ix_fda_last_observed ON fda_records(last_observed_at DESC);
    ''')


def normalize(raw: dict) -> dict:
    if not isinstance(raw,dict) or not isinstance(raw.get('recall_number'),str) or not raw['recall_number'].strip():
        raise FDAError('INVALID_FDA_RECORD','FDA record missing recall_number',422)
    return {**{k:raw.get(k) if raw.get(k) is not None else None for k in FIELDS},
            'recall_number':raw['recall_number'].strip(),
            'lot_parse_status':'UNVERIFIED_FREE_TEXT',
            'source_system':'openFDA food enforcement',
            'source_info_url':PUBLIC_INFO,
            'inventory_mapping':'NONE',
            'is_current_alert':False}


def build_url(limit: int, skip: int, search: str = '', include_key=True) -> str:
    # No arbitrary URLs and no freeform openFDA query-language injection.
    if not 1 <= limit <= 100 or skip < 0 or skip > 5000:
        raise FDAError('INVALID_QUERY','Pagination out of permitted bounds',422)
    query={'limit':str(limit),'skip':str(skip),'sort':'report_date:desc'}
    if search:
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9 \-]{0,79}',search):
            raise FDAError('INVALID_SEARCH','Use a product term containing letters, numbers, spaces or hyphens (max 80)',422)
        query['search']=f'product_description:"{search}"'
    if include_key and os.getenv('OPENFDA_API_KEY'):
        query['api_key']=os.environ['OPENFDA_API_KEY']
    return BASE+'?'+urllib.parse.urlencode(query)


def public_record_uri(recall_number: str) -> str:
    # Record-specific evidence lookup URI, WITHOUT any API credentials.
    return BASE+'?'+urllib.parse.urlencode({'search':f'recall_number:"{recall_number}"','limit':1})


def fetch_page(limit: int, skip: int, search: str='', *, sleep=time.sleep) -> list[dict]:
    url=build_url(limit,skip,search)
    req=urllib.request.Request(url,headers={'User-Agent':'FoodRecallAI-V0.2/0.2 (public FDA enforcement research)','Accept':'application/json'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=12) as response:
                payload=json.load(response)
            if not isinstance(payload,dict) or not isinstance(payload.get('results'),list):
                raise FDAError('UNEXPECTED_RESPONSE','FDA returned an unexpected JSON structure')
            return payload['results']
        except urllib.error.HTTPError as ex:
            if ex.code==404: return []  # openFDA uses HTTP 404 for no results
            if ex.code==429 or 500<=ex.code<600:
                if attempt<2:
                    sleep(min(4,2**attempt))
                    continue
                raise FDAError('FDA_UNAVAILABLE',f'FDA API returned HTTP {ex.code} after retries') from None
            raise FDAError('FDA_HTTP_ERROR',f'FDA API returned HTTP {ex.code}') from None
        except (urllib.error.URLError,TimeoutError,OSError,ValueError) as ex:
            if attempt<2:
                sleep(min(4,2**attempt))
                continue
            raise FDAError('FDA_UNREACHABLE','FDA endpoint could not be reached after bounded retries') from None
    raise FDAError('FDA_UNREACHABLE','FDA endpoint unavailable')


def upsert_records(conn:sqlite3.Connection, records:list[dict], observed_at:str | None=None) -> dict:
    observed_at=observed_at or utc()
    counts={'fetched':len(records),'inserted':0,'updated':0,'unchanged':0}
    # validate entire incoming batch before making any changes
    normalized=[(normalize(r),r) for r in records]
    seen=set()
    for norm, raw in normalized:
        rid=norm['recall_number']
        # repeated ID within the same page(s) is not an extra version
        if rid in seen: continue
        seen.add(rid)
        sha=digest(raw)
        old=conn.execute('SELECT version,content_sha256 FROM fda_records WHERE recall_number=?',(rid,)).fetchone()
        src=public_record_uri(rid)
        if old and old['content_sha256']==sha:
            conn.execute('UPDATE fda_records SET last_observed_at=? WHERE recall_number=?',(observed_at,rid))
            counts['unchanged']+=1
        else:
            version=old['version']+1 if old else 1
            if old: counts['updated']+=1
            else: counts['inserted']+=1
            conn.execute('''INSERT INTO fda_records(recall_number,normalized_json,raw_json,content_sha256,version,first_observed_at,last_observed_at,source_uri)
            VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(recall_number) DO UPDATE SET normalized_json=excluded.normalized_json,
            raw_json=excluded.raw_json,content_sha256=excluded.content_sha256,version=excluded.version,
            last_observed_at=excluded.last_observed_at,source_uri=excluded.source_uri''',
            (rid,canonical(norm),canonical(raw),sha,version,observed_at,observed_at,src))
            conn.execute('''INSERT INTO fda_record_versions VALUES(?,?,?,?,?,?,?)''',
                        (rid,version,canonical(raw),canonical(norm),sha,observed_at,src))
    return counts


def sync(conn_factory, pages:int=1, per_page:int=25, search:str='')->dict:
    if not 1<=pages<=5:
        raise FDAError('INVALID_QUERY','pages must be between 1 and 5',422)
    build_url(per_page,0,search)
    started=utc()
    with conn_factory() as c:
        c.execute('INSERT INTO fda_sync_runs(started_at,status) VALUES (?,?)',(started,'running'))
        sync_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
    collected=[]
    try:
        for page in range(pages):
            result=fetch_page(per_page,page*per_page,search)
            collected.extend(result)
            if len(result)<per_page:break
        with conn_factory() as c:
            c.execute('BEGIN IMMEDIATE')
            stats=upsert_records(c,collected)
            c.execute('UPDATE fda_sync_runs SET finished_at=?,status=?,fetched=?,inserted=?,updated=?,unchanged=? WHERE id=?',
                (utc(),'success',stats['fetched'],stats['inserted'],stats['updated'],stats['unchanged'],sync_id))
            c.commit()
        return {'sync_id':sync_id,'status':'success','source':'live openFDA API','query':'product description' if search else 'latest reports',**stats}
    except Exception as ex:
        # Do not log full URL or credential-bearing exception strings.
        code=ex.code if isinstance(ex,FDAError) else 'INGEST_FAILURE'
        with conn_factory() as c:
            c.execute('UPDATE fda_sync_runs SET finished_at=?,status=?,detail=? WHERE id=?',(utc(),'failed',code,sync_id))
        if isinstance(ex,FDAError):raise
        raise FDAError('INGEST_FAILURE','FDA ingestion failed validation or database transaction') from None


def list_records(conn,search:str='',limit:int=30,offset:int=0)->dict:
    if not 1<=limit<=100 or not 0<=offset<=10000: raise FDAError('INVALID_QUERY','Invalid listing parameters',422)
    if len(search)>80: raise FDAError('INVALID_QUERY','Search too long',422)
    q='SELECT normalized_json,version,content_sha256,first_observed_at,last_observed_at,source_uri FROM fda_records'
    params=[]
    if search:
        q+=' WHERE normalized_json LIKE ?'; params.append('%'+search.replace('%','\\%').replace('_','\\_')+'%')
        q=q.replace(' LIKE ?',' LIKE ? ESCAPE "\\"')
    count=conn.execute('SELECT COUNT(*) FROM ('+q+')',params).fetchone()[0]
    results=[]
    for row in conn.execute(q+' ORDER BY json_extract(normalized_json,"$.report_date") DESC,recall_number DESC LIMIT ? OFFSET ?',(*params,limit,offset)):
        obj=json.loads(row['normalized_json'])
        obj.update({k:row[k] for k in ('version','content_sha256','first_observed_at','last_observed_at','source_uri')})
        results.append(obj)
    return {'records':results,'total':count,'source':'persistent openFDA cache','real_records_only':True,'is_live_alert':False}


def get_record(conn,recall_number:str)->dict|None:
    row=conn.execute('SELECT * FROM fda_records WHERE recall_number=?',(recall_number,)).fetchone()
    if row is None:return None
    history=[dict(x) for x in conn.execute('SELECT version,content_sha256,observed_at,source_uri FROM fda_record_versions WHERE recall_number=? ORDER BY version DESC',(recall_number,))]
    return {'normalized':json.loads(row['normalized_json']),'raw':json.loads(row['raw_json']),
            'provenance':{k:row[k] for k in ('recall_number','source_system','source_uri','content_sha256','version','first_observed_at','last_observed_at')},
            'versions':history,'inventory_mapping':'NONE','warning':'FDA records do not establish that any simulated or private inventory lot is affected'}
