# FoodRecall AI V0.8 — শুধু তোমার করণীয় (২৪ অক্টোবর ২০২৬)

**বর্তমান ZIP একটি যাচাইকৃত local-development candidate, Final V1.0 নয়।** কাজের বাকি অংশ `V08_RELEASE_AUDIT_AND_HANDOFF.md`-এ পরিষ্কার লেখা আছে। কোনো password, API key, token, `.env`, real inventory rows অথবা personal account screenshot secrets সহ ChatGPT বা GitHub-এ পাঠাবে না।

## প্রথমে Windows-এ বাস্তবে চালাও

1. ZIP-এর `Extract All` → `foodrecall-ai` directory খোলো। `RUN_WINDOWS.bat` double click করো। Python 3.10+ এবং package installation-এর জন্য Windows internet দরকার।
2. প্রথম চালু হলে terminal-এ `LOCAL TRAINING LOGIN` password দেখাবে। **নিজের কাছেই রাখবে।** Browser `http://127.0.0.1:8000`-এ QA account দিয়ে sign in করো।
3. আলাদা সময়ে `RUN_ALL_TESTS_WINDOWS.bat` এবং `RUN_PREFLIGHT_WINDOWS.bat` চালাও। Local tests pass করলেও NVIDIA, Zetaris, FDA live এবং official Meterless upstream evaluation verified হয় না।
4. `Agent investigation`-এ প্রশ্ন করো: `Which lots have supplier uncertainty?`, `What changed?`, `What FDA archive records are cached?`. `Run details` খুলে `Scout Intent`, `contract.verified` দেখো। `Approve all warehouse holds now` টাইপ করলে Scout-এর নিরাপত্তা refusal দেখো। বাস্তব stock পরিবর্তন হবে না।
5. `Approvals & actions`-এ demo-only QA approval, evidence revision এবং stale decision block পরীক্ষা করো। Non-secret error, log এবং screenshot পাঠাতে পারো।

## External accounts — সত্যিকারের sponsor verification

**NVIDIA:** https://build.nvidia.com → entitled tool-calling Nemotron model ও key নিজের machine/host-এর environment-এ সেট করো (`NVIDIA_API_KEY`, `NVIDIA_MODEL`, optional `NVIDIA_BASE_URL`). Model/API cost/quotas আগে দেখো।

**Zetaris:** https://cloud.enterprise.zetaris.com/login → অনুমোদিত instance, read-only database/table mapping, OpenSqlQuery endpoint path ও token নিজের environment-এ সেট করো (`ZETARIS_URL`, `ZETARIS_ID_TOKEN`, `ZETARIS_QUERY_PATH`, `ZETARIS_RECALL_TABLE`, `ZETARIS_SHIPMENT_TABLE`). Tenant data owner approval ছাড়া private data ব্যবহার করবে না।

**Meterless:** Open-source Scout Intent এখানে **local engine code** হিসেবে কাজ করছে; gateway token না থাকলেও local engine চলে। Organizer যদি Meterless Runtime/Nightshift token চায়, সেটা নিজের account-এ configure করবে। `METERLESS_API_KEY` ইত্যাদি শুধু optional LLM gateway, Scout engine token নয়। Official upstream evaluation এখনো চলেনি—sponsor confirmation বা online official test দরকার।

**LangGraph:** Internet-enabled Windows-এ `\.venv\Scripts\python.exe -m pip install -r backend\requirements-agents.txt` চালিয়ে `engine=langgraph` দিয়ে fresh run/test করতে হবে; native fallback-কে LangGraph বলা যাবে না।

**FDA:** App-এ sign in করে `Public recall feed`-এর sync চালাও; verified success হলে record provenance পরীক্ষা করো। FDA Enforcement Report historical, সম্পূর্ণ live recall alert system নয়।

## Public demo / GitHub

- Local কাজ যাচাইয়ের আগে deploy নয়। `docs/SAFE_HOSTED_TRAINING_DEMO.md`-এ **synthetic-only** Render/Docker configuration দেওয়া আছে। Public demo করতে hosting credentials ও published HTTPS origin তোমাকেই দিতে হবে। Production security নয়।
- GitHub repo public করার আগে secret scan চালাও। `.env`, private SQLite DB, auth credentials, tenant responses কখনো commit করবে না।
- ১–৪ মিনিট demo **বাস্তব UI** থেকে record করবে; যেটা live নয় সেটাকে live বলবে না। Track ও organizer rules মেনে submission form fill ও submit করবে। Organizer announcement অনুযায়ী Cursor এখন optional, কিন্তু authentic work history misrepresent করবে না।
- Submission deadline তোমার দেওয়া organizer notification অনুযায়ী **২৭ অক্টোবর ২০২৬, ২৩:৪৫ UTC** — বাংলাদেশ সময় **২৮ অক্টোবর, ভোর ৫:৪৫**। Exact portal countdown আবার confirm করবে।

**তুমি যা পাঠাতে পারো:** Windows tests-এর non-secret output, Zetaris dashboard-এর secret-মুক্ত setup options, NVIDIA model entitlement name, এবং hosting provider setup status। এগুলোর ভিত্তিতে real integration blockers fix করা যাবে; local tests-কে live tests বলা যাবে না।
