@echo off
echo ========================================================
echo   Launching AI Teacher Full-Stack (FastAPI + React)
echo ========================================================

cd /d "%~dp0"

echo [1/2] Starting FastAPI Backend on http://localhost:8000 ...
start "AI Teacher Backend" cmd /k "run_backend.bat"

echo [2/2] Starting Vite React Frontend on http://localhost:5173 ...
start "AI Teacher Frontend" cmd /k "run_frontend.bat"

echo.
echo Both servers are launching in separate windows!
echo Backend:  http://localhost:8000 (Swagger docs at http://localhost:8000/docs)
echo Frontend: http://localhost:5173
echo.
timeout /t 3 >nul
start http://localhost:5173

