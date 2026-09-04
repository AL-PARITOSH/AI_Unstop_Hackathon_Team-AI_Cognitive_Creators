@echo off
echo ========================================================
echo   Starting AI Teacher FastAPI Backend (Port 8000)
echo ========================================================
cd /d "%~dp0"
"C:\Users\andan\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir backend --reload-dir src
pause

