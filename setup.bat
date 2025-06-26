@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Symphony AI Sleep Recommendation System
echo Project Setup Script
echo ========================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
) else (
    echo Warning: Not running as administrator. Some installations may fail.
    echo Consider running as administrator if you encounter issues.
    echo.
)

:: Function to check if command exists
where node >nul 2>&1
if %errorLevel% neq 0 (
    echo Node.js not found. Installing Node.js...
    echo.
    echo Please download and install Node.js from: https://nodejs.org/
    echo After installation, restart this script.
    echo.
    pause
    start https://nodejs.org/
    exit /b 1
) else (
    echo ✓ Node.js found
    node --version
)

:: Check for npm
where npm >nul 2>&1
if %errorLevel% neq 0 (
    echo ✗ npm not found. Please reinstall Node.js.
    pause
    exit /b 1
) else (
    echo ✓ npm found
    npm --version
)

:: Check for uv
where uv >nul 2>&1
if %errorLevel% neq 0 (
    echo uv not found. Installing uv...
    echo.
    
    :: Try to install uv using pip first
    where pip >nul 2>&1
    if %errorLevel% == 0 (
        echo Installing uv via pip...
        pip install uv
        if %errorLevel% neq 0 (
            echo Failed to install uv via pip. Trying PowerShell method...
            goto :install_uv_powershell
        )
    ) else (
        goto :install_uv_powershell
    )
    
    goto :check_uv_again
    
    :install_uv_powershell
    echo Installing uv via PowerShell...
    powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
    if %errorLevel% neq 0 (
        echo Failed to install uv. Please install manually from: https://docs.astral.sh/uv/getting-started/installation/
        pause
        exit /b 1
    )
    
    :check_uv_again
    :: Refresh PATH
    call refreshenv >nul 2>&1
    where uv >nul 2>&1
    if %errorLevel% neq 0 (
        echo uv installation may have succeeded but is not in PATH.
        echo Please restart your terminal or add uv to your PATH manually.
        echo You can also try running: refreshenv
        pause
        exit /b 1
    )
) else (
    echo ✓ uv found
    uv --version
)

echo.
echo ========================================
echo Setting up project dependencies...
echo ========================================
echo.

:: Setup backend
echo Setting up Python backend...
cd backend
if not exist ".venv" (
    echo Creating Python virtual environment...
    uv venv
    if %errorLevel% neq 0 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo Installing Python dependencies...
uv sync
if %errorLevel% neq 0 (
    echo Failed to install Python dependencies
    pause
    exit /b 1
)

cd ..

:: Setup frontend
echo.
echo Setting up Node.js frontend...
cd frontend

if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
    if %errorLevel% neq 0 (
        echo Failed to install Node.js dependencies
        pause
        exit /b 1
    )
) else (
    echo Node.js dependencies already installed
)

cd ..

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To start the development servers:
echo.
echo Backend (Python/Flask):
echo   cd backend
echo   uv run python main.py
echo.
echo Frontend (React/Vite):
echo   cd frontend  
echo   npm run dev
echo.
echo The frontend will be available at: http://localhost:3000
echo The backend API will be available at: http://localhost:5000
echo.
echo Would you like to start both servers now? (y/n)
set /p choice="Enter your choice: "

if /i "%choice%"=="y" (
    echo.
    echo Starting development servers...
    echo.
    
    :: Start backend in new window
    start "Backend Server" cmd /k "cd backend && uv run python main.py"
    
    :: Wait a moment for backend to start
    timeout /t 3 /nobreak >nul
    
    :: Start frontend in new window
    start "Frontend Server" cmd /k "cd frontend && npm run dev"
    
    :: Open browser
    timeout /t 5 /nobreak >nul
    start http://localhost:3000
    
    echo.
    echo Both servers are starting in separate windows...
    echo Frontend: http://localhost:3000
    echo Backend: http://localhost:5000
)

echo.
echo Setup script completed!
pause
