@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Python environment missing. First start RUN_WINDOWS.bat, then try again.
  pause
  exit /b 1
)
echo Verifying combined-question routing and related regression tests...
".venv\Scripts\python.exe" -c "from backend.answer_v07 import intent_for; q='Which lots are affected, which lots remain uncertain, and what evidence supports these classifications?'; result=intent_for(q); print('ROUTED INTENT:',result); assert result=='lot_status_evidence', 'Combined question did not route correctly'"
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pytest backend\tests\test_combined_investigation_question.py -q
if errorlevel 1 goto failed
echo.
echo PASS: Combined-question fix works in local tests.
echo Reminder: real NVIDIA/Zetaris live integrations are not verified.
pause
exit /b 0
:failed
echo.
echo FAIL: Combined-question fix verification did not pass. Inspect messages above.
pause
exit /b 1
