"""Chromium UI test with FastAPI TestClient bridge; not proof of live public browsing.
Real JS, click interactions, real app state, server login and CSRF.
"""
from pathlib import Path
import os,sys,tempfile
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
os.environ['FOODRECALL_DB']=str(Path(tempfile.mkdtemp())/'chromium04.db')
os.environ['FOODRECALL_BOOTSTRAP_PASSWORD']='BrowserOnly_QA_password_2026'
os.environ['FOODRECALL_ANALYST_PASSWORD']='BrowserOnly_Analyst_password_2026'
from backend.app import app
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright
client=TestClient(app)
css=(root/'frontend/styles.css').read_text()
locales=(root/'frontend/i18n.js').read_text().replace('export const ','const ').replace('export function ','function ')
js=(root/'frontend/app.js').read_text().replace("import {tr,locales} from './i18n.js';",'')

def bridge(url,opts):
    res=client.request(opts.get('method','GET'),url,headers=opts.get('headers') or {},content=opts.get('body'))
    return {'ok':res.is_success,'status':res.status_code,'data':res.json()}

with sync_playwright() as p:
    args={'headless':True,'args':['--no-sandbox','--disable-dev-shm-usage']}
    if Path('/usr/bin/chromium').exists():args['executable_path']='/usr/bin/chromium'
    browser=p.chromium.launch(**args)
    page=browser.new_page(viewport={'width':1366,'height':900},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.expose_function('_apiBridge',bridge)
    page.set_content(f'<html><head><meta charset="utf-8"><style>{css}</style></head><body><div id="app"></div></body></html>')
    page.evaluate('''() => {const store={}; Object.defineProperty(window,'localStorage',{value:{getItem:(k)=>store[k]||null,setItem:(k,v)=>store[k]=String(v)},configurable:true}); window.fetch=async(url,opts={})=>{const r=await window._apiBridge(url,opts);return {ok:r.ok,status:r.status,json:async()=>r.data}};}''')
    page.add_script_tag(type='module',content=locales+'\n'+js)
    page.get_by_role('heading',name='Sign in to the training workspace').wait_for(timeout=10000)
    assert page.locator('.login-card .brand-sub').inner_text() == 'Evidence-based recall investigation'
    assert 'V0.8' not in page.locator('.login-card').inner_text()
    assert page.locator('.login-card .brand-main').evaluate('(e)=>getComputedStyle(e).color') == 'rgb(23, 42, 57)'
    page.screenshot(path=str(root/'SCREENSHOT_v04_login.png'),full_page=True)
    page.locator('#login-password').fill('BrowserOnly_QA_password_2026')
    page.get_by_role('button',name='Sign in securely').click()
    page.get_by_text('Know what to do next.').wait_for(timeout=10000)
    assert page.get_by_text('qa@local.foodrecall',exact=False).count()>=1
    page.screenshot(path=str(root/'SCREENSHOT_v04_command_center.png'),full_page=True)
    page.locator('#language').select_option('bn')
    page.get_by_text('পরের কাজটি সহজেই বুঝুন।').wait_for()
    page.locator('#language').select_option('ar')
    assert page.locator('html').get_attribute('dir')=='rtl'
    page.locator('#language').select_option('en')
    page.locator('#theme').click()
    assert page.locator('html').get_attribute('data-theme')=='dark'
    page.locator('#theme').click()
    page.locator('[data-view=agentLab]').first.click()
    page.locator('#agent-question').fill('Which lots have supplier uncertainty?')
    page.locator('#agent-form button').click()
    page.locator('pre.agent-answer').get_by_text('TRAINING DATA ONLY',exact=False).wait_for(timeout=10000)
    page.screenshot(path=str(root/'SCREENSHOT_v07_agent_investigation.png'),full_page=True)
    page.locator('[data-view=investigation]').first.click()
    page.locator('[data-action=propose]').first.click()
    page.locator('[data-action=approve]').first.click()
    page.get_by_text('Approved',exact=True).wait_for()
    page.once('dialog',lambda d:d.accept())
    page.locator('[data-action=revise]').click()
    page.locator('.decision-diff summary').first.wait_for(timeout=10000)
    page.locator('.decision-diff summary').first.click()
    page.get_by_text('RB-073',exact=False).first.wait_for()
    page.screenshot(path=str(root/'SCREENSHOT_v04_decision_diff.png'),full_page=True)
    assert page.locator('[data-action=execute]').count()==0
    page.locator('[data-action=propose]').first.click()
    page.locator('[data-action=approve]').first.click()
    page.once('dialog',lambda d:d.accept())
    page.locator('[data-action=execute]').first.click()
    page.get_by_text('Inventory hold executed and verified.').wait_for(timeout=10000)
    response=client.get('/api/cases/DEMO-001/investigation').json()
    assert all(x['status']=='held' for x in response['confirmed'])
    page.locator('[data-view=publicFeed]').first.click()
    page.get_by_role('heading',name='FDA record archive').wait_for()
    page.locator('[data-view=epcisExplorer]').first.click()
    page.get_by_role('heading',name='Traceability explorer').wait_for()
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path=str(root/'SCREENSHOT_v04_mobile.png'),full_page=True)
    page.get_by_role('button',name='Sign out').click()
    page.get_by_role('heading',name='Sign in to the training workspace').wait_for()
    assert not errors,errors
    browser.close()
print('V0.4 CHROMIUM UI: VERIFIED login, actual auth cookie/CSRF, 8-locale UI switching sample, RTL, theme, agent, QA approval, stale decision diff, verified hold, FDA/EPCIS screens, mobile, logout. Bridge test, not public browsing.')
