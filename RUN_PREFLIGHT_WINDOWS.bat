@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo First run RUN_WINDOWS.bat to install the Python environment.
  pause
  exit /b 1
)
echo Running OFFLINE preflight. No secrets or network requests required.
".venv\Scripts\python.exe" scripts\preflight.py --output verification\PREFLIGHT_LOCAL.json
if errorlevel 1 echo Preflight failed - inspect terminal output.
echo File saved: verification\PREFLIGHT_LOCAL.json
pause
