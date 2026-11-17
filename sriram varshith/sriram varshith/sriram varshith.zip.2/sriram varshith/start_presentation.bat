@echo off
TITLE AEROSENSE - Classroom Presentation Launcher
COLOR 0B

echo ======================================================================
echo           AEROSENSE - LIVE CLASSROOM PRESENTATION LAUNCHER            
echo   Hyper-Local Atmospheric and Air Quality Forecasting System        
echo ======================================================================
echo.

cd /d "%~dp0"
if exist "aerosense\aerosense" (
    cd aerosense\aerosense
)

echo [1/3] Starting Python Flask AI Backend Server (Port 8000)...
start "AeroSense Flask API Server (:8000)" cmd /k "python run_backend.py"

timeout /t 3 /nobreak >nul

echo [2/3] Starting Frontend Server (Port 5173)...
cd aerosense-frontend
start "AeroSense Frontend Dev Server (:5173)" cmd /k "npm run dev"

timeout /t 3 /nobreak >nul

echo [3/3] Opening AeroSense in Web Browser...
start http://localhost:5173

echo.
echo ======================================================================
echo   SUCCESS! AeroSense is now running:
echo   - Backend API:    http://localhost:8000
echo   - API Health:     http://localhost:8000/health
echo   - Frontend UI:    http://localhost:5173
echo.
echo   Press any key to exit this launcher window (servers stay running).
echo ======================================================================
pause >nul
