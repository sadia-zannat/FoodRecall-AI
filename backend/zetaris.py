"""Safe, read-only Zetaris SQL adapter. Requires an organizer-provisioned tenant.

The Zetaris public KB documents body {select, pageLimit}, JWT idToken bearer,
requestId UUID, but endpoint paths are tenant/version dependent; supply the
EXACT working OpenSqlQuery request path from your own tenant's Postman collection.
"""
import json
import os
import re
import urllib.request
import urllib.error
import uuid

class ZetarisError(RuntimeError):pass

def configured():
    if os.getenv('ZETARIS_MODE', 'https').lower() == 'jdbc':
        from backend.zetaris_jdbc import jdbc_configured
        return jdbc_configured()
    return bool(os.getenv('ZETARIS_URL') and os.getenv('ZETARIS_ID_TOKEN') and os.getenv('ZETARIS_QUERY_PATH'))

def safe_table_name(value):
    if not re.fullmatch(r'[A-Za-z_][\w]*(\.[A-Za-z_][\w]*){1,2}', value or ''):
        raise ZetarisError('Table must be a configured, fully-qualified identifier')
    return value

class ZetarisClient:
    def __init__(self, url=None, token=None, path=None, transport=None):
        self.url=(url if url is not None else os.getenv('ZETARIS_URL','')).rstrip('/')
        self.token=token if token is not None else os.getenv('ZETARIS_ID_TOKEN','')
        self.path=path if path is not None else os.getenv('ZETARIS_QUERY_PATH','')
        self.transport=transport or urllib.request.urlopen
        if self.url and not (self.url.startswith('https://') or self.url.startswith('http://127.0.0.1:')):
            raise ZetarisError('ZETARIS_URL must be HTTPS or loopback')
        if self.path and (not self.path.startswith('/') or '://' in self.path or '?' in self.path):
            raise ZetarisError('ZETARIS_QUERY_PATH must be a validated path, not URL')

    @property
    def ready(self):return bool(self.url and self.token and self.path)

    def query(self, table, columns=('*',), page_limit=20):
        if not self.ready:raise ZetarisError('Zetaris tenant URL, idToken and query path required')
        table=safe_table_name(table)
        if not (1<=page_limit<=100):raise ZetarisError('pageLimit out of range')
        if columns!=('*',) and (not columns or any(not re.fullmatch(r'[A-Za-z_][\w]*',v) for v in columns)):
            raise ZetarisError('Invalid allowlisted column identifiers')
        query=f"SELECT {', '.join(columns)} FROM {table}"
        body=json.dumps({'select':query,'pageLimit':page_limit}).encode()
        request=urllib.request.Request(self.url+self.path,data=body,method='POST',headers={
            'Content-Type':'application/json','Authorization':'Bearer '+self.token,
            'requestId':str(uuid.uuid4())})
        try:
            with self.transport(request,timeout=12) as response: output=json.load(response)
        except (urllib.error.URLError,TimeoutError,OSError,ValueError) as exc:
            raise ZetarisError('Zetaris query failed ('+type(exc).__name__+')') from None
        if not isinstance(output,(dict,list)):
            raise ZetarisError('Unexpected Zetaris API response')
        return {'query':query,'response':output,'mode':'LIVE_TENANT_RESPONSE','page_limit':page_limit}

    def read_approved_sources(self):
        # Tables must be provisioned/mapped by the participant. Never infer a join
        # between synthetic inventory and regulatory notices from text similarity.
        names=[os.getenv('ZETARIS_RECALL_TABLE',''),os.getenv('ZETARIS_SHIPMENT_TABLE','')]
        if not all(names):raise ZetarisError('Both Zetaris table mappings are required')
        return {'recall':self.query(names[0]),'shipment':self.query(names[1]),
                'verified_product_lot_links':[],'writes_performed':0}


def active_client():
    """Select explicitly configured transport. No implicit fallback on failure."""
    mode = os.getenv('ZETARIS_MODE', 'https').lower()
    if mode == 'jdbc':
        from backend.zetaris_jdbc import ZetarisJDBCClient
        return ZetarisJDBCClient()
    if mode in ('https', 'http_api'):
        return ZetarisClient()
    raise ZetarisError('Unsupported ZETARIS_MODE (choose jdbc or https)')
