"""Real Chromium UI regression: combined question must show both lot groups.
Browser execution uses an authenticated FastAPI TestClient bridge, not a public deployment.
"""
from pathlib import Path
import os,sys,tempfile
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
os.environ['FOODRECALL_DB']=str(Path(tempfile.mkdtemp())/'browser_multipart.db')
os.environ['FOODRECALL_BOOTSTRAP_PASSWORD']='BrowserOnly_QA_password_2026'
os.environ['FOODRECALL_ANALYST_PASSWORD']='BrowserOnly_Analyst_password_2026'
from backend.app import app
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright

client=TestClient(app)
css=(root/'frontend/styles.css').read_text(encoding='utf-8')
locales=(root/'frontend/i18n.js').read_text(encoding='utf-8').replace('export const ','const ').replace('export function ','function ')
js=(root/'frontend/app.js').read_text(encoding='utf-8').replace("import {tr,locales} from './i18n.js';",'')
question='Which lots are affected, which lots remain uncertain, and what evidence supports these classifications?'

def bridge(url,opts):
    response=client.request(opts.get('method','GET'),url,headers=opts.get('headers') or {},content=opts.get('body'))
    return {'ok':response.is_success,'status':response.status_code,'data':response.json()}

with sync_playwright() as p:
    options={'headless':True,'args':['--no-sandbox','--disable-dev-shm-usage']}
    if Path('/usr/bin/chromium').exists():options['executable_path']='/usr/bin/chromium'
    browser=p.chromium.launch(**options)
    page=browser.new_page(viewport={'width':1366,'height':900})
    errors=[]
    page.on('pageerror',lambda exc:errors.append(str(exc)))
    page.expose_function('_apiBridge',bridge)
    page.set_content(f'<html><head><meta charset="utf-8"><style>{css}</style></head><body><div id="app"></div></body></html>')
    page.evaluate('''() => {const saved={}; Object.defineProperty(window,'localStorage',{value:{getItem:k=>saved[k]||null,setItem:(k,v)=>saved[k]=String(v)},configurable:true});window.fetch=async(url,opts={})=>{const r=await window._apiBridge(url,opts);return {ok:r.ok,status:r.status,json:async()=>r.data}};}''')
    page.add_script_tag(type='module',content=locales+'\n'+js)
    page.locator('#login-password').fill('BrowserOnly_QA_password_2026')
    page.get_by_role('button',name='Sign in securely').click()
    page.get_by_text('Know what to do next.').wait_for(timeout=10000)
    page.locator('[data-view=agentLab]').first.click()
    page.locator('#agent-question').fill(question)
    page.locator('#agent-form button').click()
    result=page.locator('pre.agent-answer')
    result.get_by_text('Affected in the training inventory:',exact=False).wait_for(timeout=10000)
    rendered=result.inner_text()
    for phrase in ('RB-071 (120 units)','RB-072 (85 units)','RB-073 (46 units)',
                   'Retrieved records mentioning RB-071: [E-01], [E-02]',
                   'Retrieved records mentioning RB-073: [E-02], [E-03]'):
        assert phrase in rendered,phrase
    assert page.get_by_text('Saved investigations').count()>=1
    assert not errors,errors
    browser.close()
print('CHROMIUM COMBINED QUESTION: PASS real JS, authenticated API bridge, affected + uncertain + lot-specific citations.')
