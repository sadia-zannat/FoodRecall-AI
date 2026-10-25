#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
printf '\nFoodRecall AI available at http://127.0.0.1:8000\n'
.venv/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
