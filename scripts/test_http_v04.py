"""Actual TCP localhost API, cookie login, CSRF, decision diff and read-back smoke."""
import http.cookiejar,json,os,socket,subprocess,sys,tempfile,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
BASE=f'http://127.0.0.1:{port}'
with tempfile.TemporaryDirectory() as tmp:
    env={**os.environ,'FOODRECALL_DB':str(Path(tmp)/'live_http.sqlite'),
         'FOODRECALL_BOOTSTRAP_PASSWORD':'RealHTTPOnly_QA_password_2026',
         'FOODRECALL_ANALYST_PASSWORD':'RealHTTPOnly_Analyst_password_2026'}
    server=subprocess.Popen([sys.executable,'-m','uvicorn','backend.app:app','--host','127.0.0.1','--port',str(port)],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    jar=http.cookiejar.CookieJar();client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    csrf=''
    def req(path,method='GET',body=None,token=True):
        data=json.dumps(body).encode() if body is not None else (b'{}' if method=='POST' else None)
        headers={'Content-Type':'application/json'}
        if csrf and token:headers['X-CSRF-Token']=csrf
        response=client.open(urllib.request.Request(BASE+path,headers=headers,data=data,method=method),timeout=8)
        with response as r:return r.status,json.loads(r.read())
    try:
        for _ in range(120):
            if server.poll() is not None:raise RuntimeError('server stopped before ready')
            try:assert req('/api/health')[0]==200;break
            except (OSError,AssertionError):time.sleep(.1)
        else:raise RuntimeError('server timed out')
        assert req('/api/traceability/graph')[1]['event_count']==7
        try:req('/api/cases/DEMO-001/proposals','POST',{},token=False);raise AssertionError('anonymous mutation worked')
        except urllib.error.HTTPError as exc:assert exc.code==401
        data=req('/api/auth/login','POST',{'username':'qa@local.foodrecall','password':'RealHTTPOnly_QA_password_2026'})[1]
        csrf=data['csrf_token'];assert req('/api/auth/me')[1]['user']['role']=='qa_manager'
        try:req('/api/cases/DEMO-001/proposals','POST',{},token=False);raise AssertionError('CSRF missing accepted')
        except urllib.error.HTTPError as exc:assert exc.code==403
        p=req('/api/cases/DEMO-001/proposals','POST',{})[1];pid=p['id']
        assert req(f'/api/proposals/{pid}/approve','POST',{'reviewer':'forged'})[1]['reviewer']=='qa@local.foodrecall'
        assert req('/api/cases/DEMO-001/simulate-revision','POST',{'confirm':'SIMULATE'})[0]==200
        diff=req(f'/api/proposals/{pid}/decision-diff')[1]
        assert not diff['current'] and len(diff['changes'])==2
        try:req(f'/api/proposals/{pid}/execute','POST',{});raise AssertionError('stale execution accepted')
        except urllib.error.HTTPError as exc:assert exc.code==409
        p2=req('/api/cases/DEMO-001/proposals','POST',{})[1]['id']
        assert req(f'/api/proposals/{p2}/approve','POST',{'reviewer':'QA'})[0]==200
        assert req(f'/api/proposals/{p2}/execute','POST',{})[1]['status']=='verified'
        assert req(f'/api/proposals/{p2}/execute','POST',{})[1]['idempotent_replay']
        assert len([x for x in req('/api/cases/DEMO-001/investigation')[1]['lots'] if x['status']=='held'])==3
        assert req('/api/auth/logout','POST',{})[0]==200
        try:req('/api/cases/DEMO-001/proposals','POST',{});raise AssertionError('logout not revoked')
        except urllib.error.HTTPError as exc:assert exc.code==401
        print('V0.4 REAL TCP HTTP: PASS health, EPCIS, 401 guest, cookie login, CSRF 403, approval, material revision diff, stale 409, new approval/verified hold, idempotent replay, SQLite readback, logout.')
    finally:
        server.terminate()
        try:server.wait(timeout=4)
        except subprocess.TimeoutExpired:server.kill();server.wait()
