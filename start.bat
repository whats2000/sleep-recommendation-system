@echo off
:: Simple launcher script for Symphony AI Sleep Recommendation System

echo Symphony AI Sleep Recommendation System
echo ========================================
echo.
echo Choose setup method:
echo 1. Run PowerShell setup (Recommended - better installation support)
echo 2. Run Batch setup (Basic - manual installations may be required)
echo 3. Quick start (skip setup, just start servers)
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Running PowerShell setup...
    powershell -ExecutionPolicy Bypass -File "setup.ps1"
) else if "%choice%"=="2" (
    echo.
    echo Running Batch setup...
    call setup.bat
) else if "%choice%"=="3" (
    echo.
    echo Starting servers...
    echo.
    
    :: Check if dependencies exist
    if not exist "backend\.venv" (
        echo Error: Backend not set up. Please run setup first.
        pause
        exit /b 1
    )
    
    if not exist "frontend\node_modules" (
        echo Error: Frontend not set up. Please run setup first.
        pause
        exit /b 1
    )
    
    :: Start servers
    start "Backend Server" cmd /k "cd backend && uv run python main.py"
    timeout /t 3 /nobreak >nul
    start "Frontend Server" cmd /k "cd frontend && npm run dev"
    timeout /t 5 /nobreak >nul
    start http://localhost:3000
    
    echo Servers started!
    echo Frontend: http://localhost:3000
    echo Backend: http://localhost:5000
    
) else if "%choice%"=="4" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice. Please try again.
    pause
    goto :start
)

pause
