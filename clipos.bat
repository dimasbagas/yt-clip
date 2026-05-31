@echo off
REM ClipOS CLI — call from anywhere
"%~dp0backend\.venv\Scripts\python" "%~dp0backend\clipos.py" %*
if "%*"=="" pause
if %ERRORLEVEL% NEQ 0 pause
