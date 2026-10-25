# FoodRecall AI — Corrected Full Project (24 October 2026)

এটি **combined-question answer bug সংশোধিত সম্পূর্ণ project ZIP**। এই ZIP-এ UI branding fix-ও আছে। আলাদা patch বা VS Code terminal-এ code paste করার প্রয়োজন নেই।

## কী ঠিক হয়েছে

আগে প্রশ্নটি—

> Which lots are affected, which lots remain uncertain, and what evidence supports these classifications?

—শুধু uncertain lot দেখাত। এখন নতুন investigation চালালে local synthetic fixture অনুযায়ী:

- **Affected:** RB-071 (120 units), RB-072 (85 units)
- **Uncertain:** RB-073 (46 units)
- **Retrieved evidence:** Lot-specific retrieved record IDs E-01/E-02/E-03; shipment evidence-কে allergen exposure-এর প্রমাণ বলা হয় না

পুরোনো **saved investigation** নতুন কোডে আপনা থেকে বদলাবে না। নতুন করে **Investigate** চাপতে হবে। এই ফিক্স offline rules-based agent-এ; **NVIDIA AI এখনো live নয়**।

## Windows — নতুন full ZIP খুলে চালানো

1. আগের `RUN_WINDOWS.bat`-এর server window-এ `Ctrl+C` দিয়ে বন্ধ করো; দুইটি project একই port 8000-এ চালাবে না।
2. আগের `foodrecall-ai` folder **delete বা overwrite করবে না**। সেটি old database/credentials-এর backup হিসেবে রাখো।
3. এই ZIP-টি File Explorer-এ **Extract All** করো; নতুন আলাদা location-এ রাখো। ZIP-এর ভেতরেই সম্পূর্ণ `foodrecall-ai/` folder আছে।
4. নতুন extracted `foodrecall-ai` folder-এ `RUN_WINDOWS.bat` **double-click** করো। প্রথম startup-এ Python dependencies install হতে পারে।
5. Browser-এ `http://127.0.0.1:8000` খুলবে। নতুন folder হলে terminal-এ print হওয়া **initial QA password** ব্যবহার করবে। অন্য কারও সঙ্গে password বা API key share করবে না।
6. Agent investigation-এ প্রশ্নটি লিখে **নতুন করে** `Investigate` চাপবে।
7. Optional: extracted folder-এ `VERIFY_QUESTION_FIX_WINDOWS.bat` **double-click** করলে question routing এবং সংশ্লিষ্ট backend regression tests পরীক্ষা হবে।

### আগের saved investigation/login দরকার?

নতুন folder-এ আলাদা SQLite `backend/demo.db` তৈরি হয়। পুরোনো database/history automatically migrate হয় না। আগের history অবশ্যই রাখতে চাইলে নতুন server চালানোর **আগে**, পুরোনো ও নতুন উভয় server বন্ধ রেখে, `backend/demo.db` এবং উপস্থিত থাকলে `backend/demo.db-wal`, `backend/demo.db-shm` একই নামে নতুন `backend/` folder-এ copy করতে পারো। **আগে old folder-এর আরেকটি backup রাখবে।** কোনো active server চলার সময় SQLite files copy করবে না। Project version মিললেও এই কপি production-safe database migration নয়—শুধু local training data transfer।

## যাচাই হয়েছে / হয়নি

- Backend 89/89 PASS, 50 local Scout cases PASS, 65 synthetic evidence checks PASS, TCP HTTP QA workflow PASS, Chromium combined-question UI PASS, i18n check PASS।
- ZIP integrity + clean extraction + source checksums verified. Source/evidence records are synthetic.
- Official Meterless upstream evaluation, NVIDIA live inference, Zetaris tenant SQL, genuine LangGraph runtime, FDA outbound sync এবং real-world deployment **এখনো verified নয়**। Project **V1.0 production-complete নয়**।
