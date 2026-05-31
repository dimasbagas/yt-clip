@echo off
cd /d "%~dp0backend"
echo [ClipOS] Starting backend server...
.venv\Scripts\python -m uvicorn main:app --host 127.0.0.1 --port 8899 --reload
