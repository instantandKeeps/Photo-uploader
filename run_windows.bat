@echo off
REM === Instant & Keeps Local Uploader ===
cd /d "%~dp0"
IF NOT EXIST .venv (
  echo Creating virtual environment...
  py -m venv .venv
)
call .venv\Scripts\activate
echo Installing Flask...
pip install --upgrade pip >nul
pip install flask >nul
echo Starting server on http://localhost:8080 ...
py app.py
