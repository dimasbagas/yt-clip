@echo off
echo [ClipOS] Starting backend...
cd /d "%~dp0backend"
start "" ".venv\Scripts\python" -m uvicorn main:app --host 127.0.0.1 --port 8899 --reload
echo [ClipOS] Backend starting on http://127.0.0.1:8899
echo [ClipOS] Starting frontend...
cd /d "%~dp0frontend"
start "" cmd /c "npx vite --host 2^>nul"
echo [ClipOS] Frontend starting on http://localhost:5173
echo.
echo ClipOS is starting up!
echo Frontend: http://localhost:5173
echo Backend:  http://127.0.0.1:8899
echo.
