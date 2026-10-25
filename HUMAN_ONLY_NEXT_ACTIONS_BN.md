# FoodRecall AI V0.7 — তোমার অনুমতি বা নিজের computer ছাড়া যা করা যায় না

এই ZIP-এর code, local UI, tests এবং offline AI response অংশ এখানে করা হয়েছে। **External credentials দেওয়া হয়নি, তাই live integration সম্পন্ন বলা যাবে না।**

## জরুরি করণীয় (ক্রম অনুযায়ী)

1. **Windows-এ চালাও:** ZIP Extract All → `RUN_WINDOWS.bat` → localhost login → `RUN_ALL_TESTS_WINDOWS.bat`। Screenshot ও non-secret error log শেয়ার করতে পারো। Password/API key কখনো পাঠাবে না।
2. **Zetaris চালু করো:** https://cloud.enterprise.zetaris.com/login → OTP দিয়ে লগইন → `Run Locally` থেকে অফিসিয়াল local installation অথবা billing-risk জেনে cloud cluster। Docker/local permissions প্রয়োজন। Official installer-এর commands চালানোর আগে যাচাই করো। বাস্তব read-only tenant SQL endpoint ও schema/table mapping নিজে configure করবে।
3. **NVIDIA Nemotron access:** NVIDIA API portal থেকে নিজের entitled tool-calling model ও secret key configure করো। Secret OS environment-এ থাকবে। `NVIDIA_API_KEY`, `NVIDIA_MODEL` সেট করার পরে live probe চালাবে। Paid use থাকলে আগে খরচ দেখো।
4. **বাস্তব evidence data:** অন্তত issuer-approved product GTIN/master, recall product/lot, inventory by lot/location, shipment/supplier evidence-এর lawful read-only records দরকার। শুধু FDA product name থেকে company stock confirm করা যাবে না। `docs/REAL_DATA_REQUIREMENTS.md` দেখো। Data owner approval ছাড়া private data ব্যবহার করবে না।
5. **Hackathon compliance:** প্রয়োজনীয় Cursor use-এর বাস্তব history, pre-Oct-22 prior work disclosure, নির্বাচিত track-এর eligibility, sponsor evidence, final demo video, GitHub publishing, hosted deployment সব তোমার approval/credentials ও organizer policy অনুসারে হবে।

## নিজের computer-এ provider চালু হলে যে যাচাইগুলো করতে হবে

- `RUN_PREFLIGHT_WINDOWS.bat` চালাও। এটি defaultভাবে শুধু config check; live outbound probe নিজে explicitভাবে চালাতে হবে।
- Zetaris SQL test: source tables থেকে প্রকৃত row count, schema/identifier matching; কোনো sensitive rows public করে দেবে না।
- Nemotron: real tool-selection response + source-grounded explanation-এর log; mode UI-তে সত্যিই model explanation দেখায় কিনা যাচাই।
- FDA archive: official API থেকে actual successful sync; source record ও historical limitation যাচাই।
- LangGraph: online pip install দিয়ে genuine StateGraph runtime চালিয়ে test; native fallback-এর result-কে LangGraph execution বলা যাবে না।
- Review: QA Manager evidence পরিবর্তনের পরে পুরোনো approved hold execute করতে পারে কিনা (করতে **পারবে না**)।

## এখনই করা যাবে না / কখনো মিথ্যা বলা যাবে না

- Real warehouse hold, supplier email, financial transactions বা production ERP action: permission + authorized integrations নেই।
- Public production site: local security architecture উপযুক্ত নয়।
- Final V1.0 live-sponsor-complete claim: live credentials + independently witnessed successful tests ছাড়া নয়।

> প্রথমে local Windows run-এর output এবং Zetaris account-এ `Run Locally`-এর কোনো secret-মুক্ত screenshot পাঠাও। অন্য coding handoff-এ complete project ZIP-ই basis হবে।
