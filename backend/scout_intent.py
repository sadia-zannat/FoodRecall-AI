"""FoodRecall's scoped Meterless Scout Intent engine implementation.

Implements the open-source Scout Intent AGENTS.md architectural CONTRACT for
this read-only food-recall domain: Sense -> Interpret -> Guard -> Route ->
Recommend, with locally signed 5-minute tool execution contracts. This module
is an independently authored Python adaptation, NOT the upstream TS runtime.
The upstream `npm run evals` is a separate, currently unverified acceptance gate.
Spec: https://github.com/Meterless/Meterless/blob/main/engines/scout-intent/AGENTS.md
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

REGISTRY_VERSION = 1
POLICY_VERSION = 'foodrecall-training-readonly-v1'
SURFACE = 'agent-investigation'
# In-process ephemeral signing secret; never exported or serialized to logs.
_SIGNING_KEY = secrets.token_bytes(32)

# Domain-scoped registry: examples and surface/role/capability floors are data.
# GENERAL is intentionally limited to local sources; external lookups require intent.
REGISTRY = {
    'case.overview': {'description':'Summarize the training recall case and lots',
        'examples':['Summarize this case','Give an overview','What is happening?'],
        'patterns':('overview','summary','case','what happened','investigate','investigation','সারাংশ','বিস্তারিত'),
        'capabilities':('case_notice','inventory_lots','supplier_evidence'), 'route':('case_notice','inventory_lots'), 'riskClass':'low'},
    'case.affected': {'description':'Identify affected or cleared lots and counts',
        'examples':['Which lots are affected?','How many units are affected?','কোন লট ঝুঁকিতে আছে?'],
        'patterns':('affected','lot','quantity','units','stock','inventory','risk','unsafe','clear','আক্রান্ত','ঝুঁকি','লট','ইউনিট'),
        'capabilities':('case_notice','inventory_lots','supplier_evidence'), 'route':('case_notice','inventory_lots'), 'riskClass':'low'},
    'case.supplier': {'description':'Investigate uncertainty, incomplete supplier evidence, and conflicts',
        'examples':['Which lots have supplier uncertainty?','Why is RB-073 unresolved?','সরবরাহকারীর তথ্য কেন অনিশ্চিত?'],
        'patterns':('supplier','uncertain','unresolved','incomplete','missing','conflict','rb-073','batch','evidence','citation','source','proof','অনিশ্চিত','সরবরাহ','প্রমাণ','উৎস','অমিল'),
        'capabilities':('case_notice','inventory_lots','supplier_evidence'), 'route':('case_notice','inventory_lots','supplier_evidence'), 'riskClass':'low'},
    'case.change': {'description':'Explain new evidence, change and stale QA decisions',
        'examples':['What changed in the evidence?','Check the revision and stale decision','নতুন প্রমাণ কী?'],
        'patterns':('changed','change','revision','stale','revalidate','decision diff','version','new evidence','কি পরিবর্তন','কী বদলেছে','নতুন প্রমাণ'),
        'capabilities':('case_notice','inventory_lots','supplier_evidence'), 'route':('case_notice','inventory_lots','supplier_evidence'), 'riskClass':'low'},
    'case.next_steps': {'description':'Explain safe human-reviewed training next steps without executing actions',
        'examples':['What should QA do next?','Explain the approval process','What should we do next?'],
        'patterns':('next','action','approve','approval','hold','quarantine','stop','what should','review','করণীয়','অনুমোদন','হোল্ড','কী করব'),
        'capabilities':('case_notice','inventory_lots','supplier_evidence'), 'route':('case_notice','inventory_lots','supplier_evidence'), 'riskClass':'medium'},
    'external.fda_cache': {'description':'Inspect historic cached openFDA food enforcement records',
        'examples':['What does the FDA archive say?','Check public recall evidence','এফডিএ তথ্য দেখাও'],
        'patterns':('fda','openfda','enforcement','archive','published','public recall','এফডিএ'),
        'capabilities':('case_notice','inventory_lots','supplier_evidence','cached_fda'),
        'route':('case_notice','inventory_lots','cached_fda'), 'riskClass':'low'},
    'external.zetaris': {'description':'Read preconfigured authorized Zetaris SQL evidence (no writes)',
        'examples':['Inspect Zetaris connected data','What was returned by SQL?','জেটারিস ডাটা দেখাও'],
        'patterns':('zetaris','sql','connected data','tenant database','জেটারিস'),
        'capabilities':('case_notice','inventory_lots','supplier_evidence','zetaris_sources'),
        'route':('case_notice','inventory_lots','zetaris_sources'), 'riskClass':'medium'},
    'case.traceability': {'description':'Inspect fictional EPCIS shipping event graph',
        'examples':['Trace the shipment events','Explain the EPCIS graph','শিপমেন্টের তথ্য'],
        'patterns':('shipment','epcis','traceability','transport','supply chain','শিপমেন্ট','ট্রেস'),
        'capabilities':('case_notice','inventory_lots','supplier_evidence','synthetic_epcis'),
        'route':('case_notice','inventory_lots','synthetic_epcis'), 'riskClass':'low'},
}
# Full matching words/phrases, NOT substrings of arbitrary text (avoid 'lot' in 'pilot').
_BYPASS = re.compile(r'</?system\b|\[/?INST\]|ignore (?:all |the |previous )?(?:system |safety |previous )?instructions|(?:reveal|print|show me|give me) (?:the |your )?(?:api key|secret|system prompt)|(?:disable|bypass) (?:all )?(?:safety|policy|guard)|developer mode',re.I)
_UNSAFE_ACTION = re.compile(r'\b(?:please\s+)?(?:execute|perform|trigger|initiate|issue|send|delete|write|update|change|approve|authorize|release|ship)\b[^.!?\n]{0,65}\b(?:warehouse|inventory|stock|hold|erp|supplier email|production)\b|\b(?:approve|execute)\s+(?:all\s+)?(?:the\s+)?(?:holds|warehouse holds)\b',re.I)
_SENSITIVE = re.compile(r'\b(?:sk-[A-Za-z0-9_-]{12,}|Bearer\s+[A-Za-z0-9_.-]{12,})\b',re.I)

class ScoutDenied(ValueError):
    """No capability was issued; the executor must fail closed."""


def _utc(when):
    return datetime.fromtimestamp(when,tz=timezone.utc).isoformat(timespec='seconds')


def _canonical(payload):
    return json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')


def _hit(question, phrase):
    return bool(re.search(r'(?<!\w)'+re.escape(phrase)+r'(?!\w)',question,re.I))


def sense(question, prior=()):
    """Fast deterministic stage 1. Stage 2 semantic rescorer not claimed.

    Earlier questions supply context only for short follow-ups and cannot grant
    capabilities themselves. The denominator is local lexical matched strength,
    NOT a model probability calibrated against real users.
    """
    raw=question.casefold()
    if raw.strip() in ('why?','why','explain','কেন?','কেন','আরও বলো','what about that?','why is that?') and prior:
        raw=(str(prior[-1])+' '+raw).casefold()
    scored=[]
    for intent,meta in REGISTRY.items():
        phrases=[p for p in meta['patterns'] if _hit(raw,p)]
        weighted=sum(1+min(len(p),15)/15 for p in phrases)
        scored.append({'intent':intent,'score':weighted,'matched':phrases})
    scored.sort(key=lambda x:(-x['score'],x['intent']))
    if scored[0]['score']<=0:
        return {'intent':'case.overview','confidence':0.0,'band':'reject','candidates':scored[:3], 'stage2':'unavailable'}
    top=scored[0]['score']
    # Deterministic normalized lexical confidence; not the optional semantic formula.
    confidence=round(min(1., 0.62+0.12*len(scored[0]['matched'])+0.04*min(top,2)),3)
    band='high' if confidence>=.80 else 'medium' if confidence>=.55 else 'low' if confidence>=.40 else 'reject'
    return {'intent':scored[0]['intent'],'confidence':confidence,'band':band,
            'candidates':scored[:3],'stage2':'unavailable'}


def interpret(question, case_id, sense_result):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,60}',case_id):raise ScoutDenied('invalid-case')
    return {'parameters':{'case_id':case_id},'references':{'case':{'id':case_id,'type':'training_case'}},
            'clarification':sense_result['band']=='low'}


def guard(question, intent, role='analyst', surface=SURFACE):
    if role not in ('analyst','qa_manager','auditor') or surface!=SURFACE:
        return {'level':'block','flags':['scope_or_role_denied'],'redactions':[],'reason':'scope_mismatch'}
    flags=[]
    if _BYPASS.search(question): flags.append('prompt_injection')
    if _UNSAFE_ACTION.search(question): flags.append('operational_action_not_authorized')
    if _SENSITIVE.search(question): flags.append('sensitive_token_in_prompt')
    if flags:
        return {'level':'block','flags':flags,'redactions':[],'reason':flags[0]}
    return {'level':REGISTRY[intent]['riskClass'],'flags':[],'redactions':[], 'reason':None}


def route(intent, configured_sources=(), requested=None):
    """Resolve the capability graph to concrete read-only tools.

    Requested tool plans must be subsets of the intent's capability floor.
    Optional Zetaris transport is removed unless specifically configured.
    """
    meta=REGISTRY[intent]
    available=set(configured_sources)|{'case_notice','inventory_lots','supplier_evidence','cached_fda','synthetic_epcis'}
    allowed=set(meta['capabilities'])&available
    steps=list(requested if requested is not None else meta['route'])
    if len(steps)!=len(set(steps)) or any(x not in allowed for x in steps):
        raise ScoutDenied('tool_outside_scoped_capability')
    return steps


def issue(question, case_id, *, requested=None, prior=(), role='analyst',
          configured_sources=(), parent=None, now=None, trace_id=None):
    """Sign a fresh immutable scope for one bounded agent planning step."""
    if not isinstance(question,str) or not 1<=len(question.strip())<=1400:
        raise ScoutDenied('invalid-question')
    start=time.perf_counter()
    classified=sense(question,prior)
    bound=interpret(question,case_id,classified)
    policy=guard(question,classified['intent'],role=role)
    if policy['level']=='block':raise ScoutDenied(policy['reason'])
    steps=route(classified['intent'],configured_sources,requested)
    moment=time.time() if now is None else now
    issued={
        'contractId':uuid.uuid4().hex,'parentId':parent,'traceId':trace_id or uuid.uuid4().hex,
        'intent':{'primary':{'id':classified['intent'],'version':REGISTRY_VERSION},
                  'parameters':bound['parameters'],'references':bound['references'],
                  'confidence':classified['confidence'],
                  'alternates':[{'id':x['intent'],'score':x['score']} for x in classified['candidates'][1:]]},
        'risk':{'level':policy['level'],'flags':policy['flags'],'redactions':policy['redactions'],'approvals':[]},
        'toolPlan':[{'tool':x,'input':{}} for x in steps],
        'modelProfile':{'id':'local_first_optional_model'},
        'scope':{'user':{'role':role},'surface':SURFACE,'capabilities':list(steps)},
        'issuedAt':_utc(moment),'expiresAt':_utc(moment+300),'registryVersion':REGISTRY_VERSION,
        'policyPackVersion':POLICY_VERSION,'signedBy':'scout',
    }
    issued['signature']=hmac.new(_SIGNING_KEY,_canonical(issued),hashlib.sha256).hexdigest()
    return issued,{'intent':classified['intent'],'band':classified['band'],
                   'confidence':classified['confidence'],'stage2':'unavailable',
                   'duration_ms':round((time.perf_counter()-start)*1000,2),'allowed_tools':steps,
                   'risk_level':policy['level'],'clarification':bound['clarification']}


def verify(contract, tool, *, now=None):
    """Called at the executor boundary, not trusted because the planner said yes."""
    if not isinstance(contract,dict) or 'signature' not in contract:return False
    unsigned={k:v for k,v in contract.items() if k!='signature'}
    signed=hmac.new(_SIGNING_KEY,_canonical(unsigned),hashlib.sha256).hexdigest()
    if not hmac.compare_digest(str(contract['signature']),signed):return False
    if contract.get('signedBy')!='scout' or contract.get('registryVersion')!=REGISTRY_VERSION:return False
    if contract.get('policyPackVersion')!=POLICY_VERSION:return False
    try:
        expires=datetime.fromisoformat(contract['expiresAt']).timestamp()
        issued=datetime.fromisoformat(contract['issuedAt']).timestamp()
    except (ValueError,TypeError,KeyError):return False
    moment=time.time() if now is None else now
    if expires<=moment or issued>moment+5:return False
    if expires-issued>301:return False
    if contract.get('risk',{}).get('level')=='high' and not contract['risk'].get('approvals'):return False
    if contract.get('scope',{}).get('surface')!=SURFACE:return False
    plan=[step.get('tool') for step in contract.get('toolPlan',[]) if isinstance(step,dict)]
    caps=contract.get('scope',{}).get('capabilities',[])
    return tool in plan and tool in caps


def selftest():
    """Spec's 16ms stage-1 budget measured on relevant local probes."""
    probes=['Which lots have supplier uncertainty?', 'Read FDA archive', 'Show shipment EPCIS graph',
            'What changed since the new evidence?', 'কোন লট ঝুঁকিতে আছে?']
    samples=[]
    for prompt in probes:
        begin=time.perf_counter();sense(prompt);samples.append(round((time.perf_counter()-begin)*1000,3))
    return {'budget_ms':16,'max_observed_ms':max(samples),'passed':max(samples)<16,'probes':len(probes)}
