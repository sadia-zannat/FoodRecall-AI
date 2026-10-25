@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
if not exist ".venv\Scripts\python.exe" (
  echo Creating Python environment...
  %PY% -m venv .venv
  if errorlevel 1 (echo ERROR: Python 3.10+ is required. & pause & exit /b 1)
)
".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
if errorlevel 1 (echo ERROR: Dependency installation failed. Check internet access. & pause & exit /b 1)
echo.
echo FoodRecall AI starting at http://127.0.0.1:8000
start "" cmd /c "timeout /t 3 >nul & start http://127.0.0.1:8000"
".venv\Scripts\python.exe" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
echo Server stopped.
pause
