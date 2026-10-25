"""Selective evidence-bound decision snapshot and explainable revalidation.

The rule is intentionally conservative: a newly affected OR uncertain lot can
change scope. Unrelated notes or harmless audit events do not invalidate it.
Only deterministic server logic has warehouse write authority.
"""
from __future__ import annotations
import hashlib,json

CRITICAL_KINDS={'training_notice','shipment_manifest','supplier_response'}

def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'))

def context(c,case_id):
    lots=c.execute('SELECT id,classification,location,quantity FROM lots WHERE case_id=? ORDER BY id',(case_id,)).fetchall()
    evidence=c.execute('SELECT id,kind,version,detail FROM evidence WHERE case_id=? ORDER BY id',(case_id,)).fetchall()
    return {
      'scope_lots':[{k:r[k] for k in ('id','classification','location','quantity')} for r in lots if r['classification'] in ('affected','uncertain')],
      'critical_evidence':[{k:r[k] for k in ('id','kind','version','detail')} for r in evidence if r['kind'] in CRITICAL_KINDS]
    }

def digest(ctx):return hashlib.sha256(canonical(ctx).encode()).hexdigest()

def init_tables(c):
    c.execute('''CREATE TABLE IF NOT EXISTS proposal_dependencies (
      proposal_id INTEGER PRIMARY KEY REFERENCES proposals(id) ON DELETE CASCADE,
      context_json TEXT NOT NULL,context_hash TEXT NOT NULL)''')

def capture(c,pid,case_id):
    ctx=context(c,case_id)
    c.execute('INSERT INTO proposal_dependencies(proposal_id,context_json,context_hash) VALUES (?,?,?)',(pid,canonical(ctx),digest(ctx)))
    return digest(ctx)

def compare(c,p):
    record=c.execute('SELECT * FROM proposal_dependencies WHERE proposal_id=?',(p['id'],)).fetchone()
    current_ctx=context(c,p['case_id'])
    if not record:
        # Earlier V0.1/V0.2/V0.3 approvals may not be migrated; fail closed.
        return {'current':False,'legacy_without_dependencies':True,'old_hash':p['snapshot'],
                'new_hash':digest(current_ctx),'changes':[{'field':'legacy','message':'Reinvestigate and recreate this pre-V0.4 proposal'}]}
    old=json.loads(record['context_json']);new=digest(current_ctx)
    if record['context_hash']==new:
        return {'current':True,'old_hash':record['context_hash'],'new_hash':new,'changes':[]}
    changes=[]
    for label,key in [('lot','scope_lots'),('evidence','critical_evidence')]:
        before={r['id']:r for r in old[key]};after={r['id']:r for r in current_ctx[key]}
        for identifier in sorted(set(before)|set(after)):
            if before.get(identifier)!=after.get(identifier):
                changes.append({'field':label,'id':identifier,'old':before.get(identifier),'new':after.get(identifier)})
    return {'current':False,'old_hash':record['context_hash'],'new_hash':new,'changes':changes}
