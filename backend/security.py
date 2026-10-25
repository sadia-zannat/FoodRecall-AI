"""V0.4 local training identity and session boundary.

NOT an enterprise IAM product. Passwords hashed, sessions opaque/hashed at rest,
HttpOnly/SameSite cookies, CSRF guard and explicit RBAC. Local writes only.
"""
from __future__ import annotations
import hashlib, hmac, os, secrets, sqlite3, time
from datetime import datetime, timezone
from fastapi import HTTPException

ITERATIONS=260_000
ROLES={'analyst','qa_manager','auditor'}
SESSION_TTL=8*3600

def _hash_password(password,salt):
    return hashlib.pbkdf2_hmac('sha256',password.encode('utf-8'),bytes.fromhex(salt),ITERATIONS).hex()

def _digest(token):return hashlib.sha256(token.encode()).hexdigest()

def initialize(c):
    c.executescript('''
    CREATE TABLE IF NOT EXISTS auth_users (
      id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE,
      salt TEXT NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL,
      organization TEXT NOT NULL DEFAULT 'training', disabled INTEGER NOT NULL DEFAULT 0,
      failed_attempts INTEGER NOT NULL DEFAULT 0, locked_until INTEGER NOT NULL DEFAULT 0);
    CREATE TABLE IF NOT EXISTS auth_sessions (
      token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES auth_users(id),
      csrf_token TEXT NOT NULL, expires INTEGER NOT NULL, created INTEGER NOT NULL);
    CREATE TABLE IF NOT EXISTS auth_audit (
      id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL, username TEXT,
      timestamp TEXT NOT NULL, detail TEXT NOT NULL);
    ''')
    existing=c.execute('SELECT COUNT(*) FROM auth_users').fetchone()[0]
    if existing:return
    for name,role,env in [('qa@local.foodrecall','qa_manager','FOODRECALL_BOOTSTRAP_PASSWORD'),('analyst@local.foodrecall','analyst','FOODRECALL_ANALYST_PASSWORD')]:
        password=os.getenv(env) or secrets.token_urlsafe(16)
        create_user(c,name,password,role)
        if not os.getenv(env):
            print(f'\n[LOCAL TRAINING LOGIN - shown only during FIRST START] {name}  /  {password}\n',flush=True)
    print('[SECURITY] Store the first-start password privately; to reset use python scripts/manage_users.py',flush=True)

def create_user(c,username,password,role):
    username=username.strip().lower()
    if role not in ROLES:raise ValueError('Invalid role')
    if len(password)<12:raise ValueError('Password must contain at least 12 characters')
    if len(username)>120 or '@' not in username:raise ValueError('Use an email-style username')
    salt=secrets.token_hex(16)
    c.execute('INSERT INTO auth_users(username,salt,password_hash,role) VALUES (?,?,?,?)',
              (username,salt,_hash_password(password,salt),role))

def reset_password(c,username,new_password):
    if len(new_password)<12:raise ValueError('Password must contain at least 12 characters')
    salt=secrets.token_hex(16)
    cur=c.execute('UPDATE auth_users SET salt=?,password_hash=?,failed_attempts=0,locked_until=0 WHERE username=?',
                  (salt,_hash_password(new_password,salt),username.strip().lower()))
    if not cur.rowcount:raise ValueError('User not found')
    c.execute('DELETE FROM auth_sessions WHERE user_id=(SELECT id FROM auth_users WHERE username=?)',(username.strip().lower(),))

def audit(c,event,username,detail=''):
    c.execute('INSERT INTO auth_audit(event,username,timestamp,detail) VALUES (?,?,?,?)',
              (event,username,datetime.now(timezone.utc).isoformat(),detail[:160]))

def login(c,username,password):
    username=username.strip().lower()
    user=c.execute('SELECT * FROM auth_users WHERE username=?',(username,)).fetchone()
    # Constant work even for unknown accounts to avoid simple timing differences.
    if not user:
        _hash_password(password,'00'*16)
        audit(c,'login_denied',username)
        raise HTTPException(401,'Invalid login or account temporarily locked')
    if user['disabled'] or user['locked_until']>int(time.time()):
        audit(c,'login_denied',username)
        raise HTTPException(401,'Invalid login or account temporarily locked')
    if not hmac.compare_digest(_hash_password(password,user['salt']),user['password_hash']):
        attempts=user['failed_attempts']+1
        c.execute('UPDATE auth_users SET failed_attempts=?,locked_until=? WHERE id=?',
                  (0 if attempts>=5 else attempts,int(time.time())+600 if attempts>=5 else 0,user['id']))
        audit(c,'login_denied',username)
        raise HTTPException(401,'Invalid login or account temporarily locked')
    c.execute('UPDATE auth_users SET failed_attempts=0,locked_until=0 WHERE id=?',(user['id'],))
    token=secrets.token_urlsafe(36);csrf=secrets.token_urlsafe(28)
    now=int(time.time())
    c.execute('DELETE FROM auth_sessions WHERE expires<?',(now,))
    c.execute('INSERT INTO auth_sessions(token_hash,user_id,csrf_token,expires,created) VALUES (?,?,?,?,?)',
              (_digest(token),user['id'],csrf,now+SESSION_TTL,now))
    audit(c,'login_succeeded',username)
    return {'token':token,'csrf':csrf,'user':{'username':username,'role':user['role'],'organization':user['organization']}}

def current(c,cookie):
    if not cookie:return None
    r=c.execute('''SELECT u.username,u.role,u.organization,u.disabled,s.csrf_token,s.expires
      FROM auth_sessions s JOIN auth_users u ON s.user_id=u.id WHERE s.token_hash=?''',(_digest(cookie),)).fetchone()
    if not r or r['disabled'] or r['expires']<=int(time.time()):return None
    return dict(r)

def authenticate(c,cookie,csrf=None,write=False,required_role=None):
    user=current(c,cookie)
    if user is None:raise HTTPException(401,'Sign in to continue')
    if user['organization']!='training':raise HTTPException(403,'Organization boundary mismatch')
    if write and (not csrf or not hmac.compare_digest(user['csrf_token'],csrf)):
        raise HTTPException(403,'Invalid or missing CSRF token')
    if required_role and user['role'] not in required_role:raise HTTPException(403,'Insufficient permissions for this role')
    return {k:user[k] for k in ('username','role','organization')}
