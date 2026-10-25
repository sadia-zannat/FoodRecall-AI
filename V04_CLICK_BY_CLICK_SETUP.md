# FoodRecall AI V0.4 — Windows + Sponsor Access (বাংলা Click-by-Click)

## A. V0.4 নিজে চালিয়ে দেখো

1. ZIP download করে right-click → **Extract All** → **Extract**।
2. ভেতরের **foodrecall-ai** folder খুলে **RUN_WINDOWS.bat** double-click। প্রথমবার packages install হওয়ার জন্য Internet লাগবে।
3. Terminal-এ প্রথমবার **LOCAL TRAINING LOGIN** অংশে QA ও analyst account-এর password দেখা যাবে। **নিজের private password manager-এ রাখো; আমাকে বা GitHub-এ দেবে না।**
4. Browser-এ `http://127.0.0.1:8000` → login email `qa@local.foodrecall` → terminal-এর QA password → **Sign in securely**।
5. বাঁ দিকের **Investigation** → lots ও evidence দেখো → **Create hold proposal**।
6. **Approvals & actions** → **Approve** → **Simulate evidence update** → পুরোনো proposal-এ **Decision Diff** খুলে RB-073/E-03 পরিবর্তন দেখো। পুরোনো approval দিয়ে Execute আর করা যাবে না।
7. **Create hold proposal** আবার → **Approve** → **Execute hold** → confirm → status `verified` → **Activity log**-এ receipt। সবই *fictional training inventory*।
8. ওপরের **Sign out** → নতুন account দিয়ে sign in করো। Analyst account দিয়ে **Approve** / **Execute** disabled এবং server-এ 403 হওয়া উচিত।
9. Password হারালে project folder-এ Shift + Right Click → **Open in Terminal** → `.\.venv\Scripts\python.exe scripts\manage_users.py` → email ও নতুন password input। Password টাইপ করার সময় terminal-এ অক্ষর দেখাবে না।

## B. Cursor-এ actual development (official requirement)

1. [cursor.com/downloads](https://cursor.com/downloads) খুলে **Windows Download** → installer run → Cursor launch → sign in।
2. Cursor menu **File → Open Folder** → extracted **foodrecall-ai** directory select। Project files editor sidebar-এ দেখা যাবে।
3. Cursor-এ `Ctrl+I` → Agent chat → *'Inspect backend/security.py and backend/decision_v04.py, add a meaningful missing security regression test and run pytest. Explain each change. Do not touch credentials.'* লিখে submit। Changes review করে গ্রহণ করো।
4. Terminal → **New Terminal** → `.\.venv\Scripts\python.exe -m pytest backend\tests -q` → outcome record করো।
5. Git repository-তে **actual Cursor-authored changes**, truthful README note ও commit history রেখে দাও। ChatGPT-generated code-কে আগে থেকে Cursor-generated বলে claim করবে না।

## C. NVIDIA Nemotron—live test

1. [NVIDIA API Catalog](https://build.nvidia.com/) → **Sign In** → নিজের NVIDIA account।
2. Nemotron capable model-এর page খুলে **Get API Key** → account authorization complete → key privateভাবে save। Model page-এ actual **model ID** এবং **tool-calling support** verify করো। Not all NVIDIA models support every tool feature.
3. `foodrecall-ai` folder-এর PowerShell-এ:

```powershell
$sec=Read-Host 'NVIDIA key' -AsSecureString
$env:NVIDIA_API_KEY=[System.Net.NetworkCredential]::new('', $sec).Password
$env:NVIDIA_MODEL='COPY_ACTUAL_NEMOTRON_MODEL_ID_FROM_CATALOG'
$env:NVIDIA_BASE_URL='https://integrate.api.nvidia.com/v1'
.\.venv\Scripts\python.exe scripts\check_live_integrations.py --nvidia
```

4. Live probe `LIVE_RESPONSE_OBSERVED` দেখালে *text inference access* প্রতিষ্ঠিত হয়; তারপর **same terminal**-এ app run করে Agent Investigation screen-এ question দাও। `/api/agent/chat` result-এর `selection_mode` real `model_tool_calls` এবং trace-এ tool execution evidence যাচাই করো। এটি না পাওয়া পর্যন্ত genuine LLM-directed tool use VERIFIED নয়।
5. ভুল key, rate limit, model entitlement ও tool-schema errors `BLOCKERS.md`-এ লিখো। Key chat, screenshot, README বা repository-তে paste করবে না।

## D. Zetaris—actual tenant and data

1. [HackOS Resources](https://hackathon.genai.works/resources) → **Zetaris** sponsor folder → access instructions/tenant login। নিজের account দিয়ে login করো; কোনো tenant automatically অনুমান করবে না।
2. Zetaris NDP Fabric Builder-এর data source registration flow-তে **two legitimate sources** register করো: e.g. your staged recall archive table and **synthetic-labelled** shipment event table. Real private company data permission ছাড়া upload করো না।
3. **SQL Editor** খুলে registered tables থেকে sample `SELECT` query চালিয়ে বাস্তব rows পাও কি না verify করো। SQL Editor-এ correct datasource.table name নাও।
4. [Zetaris REST API Guide](https://kbase.zetaris.com/knowledge/rest-api) → Postman collection/environment download/import। Postman-এ **Import** → collection & environment → environment's tenant URL, admin account (personal only) → **Auth → Login → Send**; idToken auto populated হলে **DBQuery → OpenSqlQuery → Body**-তে `{"select":"SELECT * FROM your_source.table","pageLimit":2}` → **Send**। Response rows confirm করো।
5. Postman OpenSqlQuery-এর **exact tenant-specific request path** দেখে app env configure করো:

```powershell
$env:ZETARIS_URL='https://YOUR_REAL_APPROVED_TENANT'
$env:ZETARIS_QUERY_PATH='/REAL_OpenSqlQuery_PATH_FROM_POSTMAN'
$sec=Read-Host 'Zetaris idToken' -AsSecureString
$env:ZETARIS_ID_TOKEN=[System.Net.NetworkCredential]::new('', $sec).Password
$env:ZETARIS_RECALL_TABLE='YOUR_RECALL_SOURCE.table'
$env:ZETARIS_SHIPMENT_TABLE='YOUR_SHIPMENT_SOURCE.table'
.\.venv\Scripts\python.exe scripts\check_live_integrations.py --zetaris
```

6. Actual SQL response দেখলেই **live connectivity** verified; কিন্তু FDA-to-private-lot verified join, automatic holds বা product-level accuracy তখনো প্রমাণিত নয়। `/api/zetaris/test-query` authenticated QA/analyst session দিয়ে call করা যায়; never paste credentials into screenshots. API token expire করলে Postman Login থেকে refresh করতে হবে।

## E. LangGraph

1. Project folder-এর PowerShell → `.\.venv\Scripts\python.exe -m pip install -r backend\requirements-agents.txt`।
2. App restart → browser-এ `http://127.0.0.1:8000/api/agent/status` → `langgraph_import_available` true কিনা দেখো।
3. Agent Investigation-এ new question → result `graph_engine` = `langgraph_stategraph` হলে actual runtime verified; না হলে `native_fallback_not_langgraph` থাকবে।
4. Eval/test suite আবার চালাও: `.\.venv\Scripts\python.exe -m pytest backend\tests -q`।

## F. FDA & final judging requirements

1. App → **Public recall feed** → **Sync latest FDA records**। API internet পাওয়া গেলে real record, hash, provenance, original payload, history দেখাবে। এ পরিবেশে live unavailable ছিল।
2. Two-or-more sponsor data sources এবং actual Nemotron tool execution **same investigation trace**-এ দেখাতে হবে; model response দেখে কখনো অনুমান করবে না।
3. [HackOS submission](https://hackathon.genai.works/dashboard) এ submit-এর আগে **public GitHub source**, README, Slide Deck, **1–4 minute real demo**, sponsor proof, pre-existing-work declaration, clean clone/Docker, full judge dataset/evaluation ready করো।
4. V0.1–V0.4 সবটাই 22 Oct 2026-এর আগের কাজ: **mandatory pre-existing declaration**। Primary track-এ existing prototype permitted কিনা clarification দরকার, Wildcard option আলাদা। Organizer-কে HackOS #help desk বা `hackathons@genai.works`-এ জিজ্ঞেস করো।
5. End-to-end public production launch: current local-only training auth ও SQLite **যথেষ্ট নয়**। Cloud-safe auth/tenant DB/role policies/secure TLS/audit/CI secret scan + independent tests ছাড়া public mutation endpoints deploy করবে না।

**Deadline:** 27 October 2026 at 23:45 UTC = Bangladesh 28 October সকাল 05:45।
