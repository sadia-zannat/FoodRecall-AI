@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Missing .venv. Double-click RUN_WINDOWS.bat first, then close the server.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m pytest backend\tests -q
if errorlevel 1 goto failed
".venv\Scripts\python.exe" scripts\evaluate_scout.py
if errorlevel 1 goto failed
".venv\Scripts\python.exe" scripts\evaluate_release.py
if errorlevel 1 goto failed
".venv\Scripts\python.exe" scripts\test_http_v04.py
if errorlevel 1 goto failed
where node >nul 2>nul
if %errorlevel%==0 (
  node scripts\test_i18n.mjs
  if errorlevel 1 goto failed
  node scripts\test_v02_locales.mjs
  if errorlevel 1 goto failed
  node scripts\test_user_branding.mjs
  if errorlevel 1 goto failed
) else (
  echo SKIPPED locale validators: Node.js not installed.
)
echo.
echo LOCAL V0.8 QA PASSED. This does NOT verify official Meterless evals or live NVIDIA/Zetaris/FDA.
pause
exit /b 0
:failed
echo OFFLINE QA FAILED. Inspect output above.
pause
exit /b 1
