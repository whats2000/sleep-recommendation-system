# Symphony AI Sleep Recommendation System - Setup Script
# PowerShell version for enhanced functionality

param(
    [switch]$SkipNodeInstall,
    [switch]$SkipUvInstall,
    [switch]$AutoStart
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Symphony AI Sleep Recommendation System" -ForegroundColor Cyan
Write-Host "Project Setup Script (PowerShell)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (Test-Administrator) {
    Write-Host "✓ Running with administrator privileges" -ForegroundColor Green
} else {
    Write-Host "⚠ Warning: Not running as administrator. Some installations may fail." -ForegroundColor Yellow
    Write-Host "Consider running as administrator if you encounter issues." -ForegroundColor Yellow
    Write-Host ""
}

# Function to check if command exists
function Test-Command($command) {
    try {
        Get-Command $command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Function to install Node.js using winget or chocolatey
function Install-NodeJS {
    Write-Host "Installing Node.js..." -ForegroundColor Yellow
    
    # Try winget first (Windows 10/11)
    if (Test-Command "winget") {
        Write-Host "Installing Node.js via winget..." -ForegroundColor Blue
        try {
            winget install OpenJS.NodeJS
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Node.js installed successfully via winget" -ForegroundColor Green
                return $true
            }
        } catch {
            Write-Host "Failed to install via winget, trying alternative methods..." -ForegroundColor Yellow
        }
    }
    
    # Try chocolatey
    if (Test-Command "choco") {
        Write-Host "Installing Node.js via Chocolatey..." -ForegroundColor Blue
        try {
            choco install nodejs -y
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Node.js installed successfully via Chocolatey" -ForegroundColor Green
                return $true
            }
        } catch {
            Write-Host "Failed to install via Chocolatey" -ForegroundColor Red
        }
    }
    
    # Manual download fallback
    Write-Host "Please download and install Node.js manually from: https://nodejs.org/" -ForegroundColor Yellow
    Start-Process "https://nodejs.org/"
    Read-Host "Press Enter after installing Node.js to continue"
    return Test-Command "node"
}

# Function to install uv
function Install-Uv {
    Write-Host "Installing uv..." -ForegroundColor Yellow
    
    try {
        # Official uv installation script
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
        
        # Refresh environment variables
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        
        if (Test-Command "uv") {
            Write-Host "✓ uv installed successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "uv installation completed but not found in PATH. Please restart your terminal." -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "Failed to install uv. Error: $_" -ForegroundColor Red
        Write-Host "Please install manually from: https://docs.astral.sh/uv/getting-started/installation/" -ForegroundColor Yellow
        return $false
    }
}

# Check Node.js
if (-not $SkipNodeInstall) {
    if (Test-Command "node") {
        Write-Host "✓ Node.js found" -ForegroundColor Green
        $nodeVersion = node --version
        Write-Host "  Version: $nodeVersion" -ForegroundColor Gray
    } else {
        if (-not (Install-NodeJS)) {
            Write-Host "✗ Failed to install Node.js. Exiting." -ForegroundColor Red
            exit 1
        }
    }
    
    # Check npm
    if (Test-Command "npm") {
        Write-Host "✓ npm found" -ForegroundColor Green
        $npmVersion = npm --version
        Write-Host "  Version: $npmVersion" -ForegroundColor Gray
    } else {
        Write-Host "✗ npm not found. Please reinstall Node.js." -ForegroundColor Red
        exit 1
    }
}

# Check uv
if (-not $SkipUvInstall) {
    if (Test-Command "uv") {
        Write-Host "✓ uv found" -ForegroundColor Green
        $uvVersion = uv --version
        Write-Host "  Version: $uvVersion" -ForegroundColor Gray
    } else {
        if (-not (Install-Uv)) {
            Write-Host "✗ Failed to install uv. Exiting." -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up project dependencies..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Setup backend
Write-Host "Setting up Python backend..." -ForegroundColor Blue
Push-Location "backend"

try {
    if (-not (Test-Path ".venv")) {
        Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
        uv venv
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
    }
    
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    uv sync
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install Python dependencies"
    }
    
    Write-Host "✓ Backend setup completed" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend setup failed: $_" -ForegroundColor Red
    Pop-Location
    exit 1
} finally {
    Pop-Location
}

# Setup frontend
Write-Host ""
Write-Host "Setting up Node.js frontend..." -ForegroundColor Blue
Push-Location "frontend"

try {
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
        npm install
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install Node.js dependencies"
        }
    } else {
        Write-Host "✓ Node.js dependencies already installed" -ForegroundColor Green
    }
    
    Write-Host "✓ Frontend setup completed" -ForegroundColor Green
} catch {
    Write-Host "✗ Frontend setup failed: $_" -ForegroundColor Red
    Pop-Location
    exit 1
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the development servers:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend (Python/Flask):" -ForegroundColor Yellow
Write-Host "  cd backend" -ForegroundColor Gray
Write-Host "  uv run python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Frontend (React/Vite):" -ForegroundColor Yellow
Write-Host "  cd frontend" -ForegroundColor Gray
Write-Host "  npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "URLs:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "  Backend:  http://localhost:5000" -ForegroundColor Gray
Write-Host ""

# Auto-start option
if ($AutoStart) {
    $startServers = $true
} else {
    $choice = Read-Host "Would you like to start both servers now? (y/n)"
    $startServers = $choice -match "^[Yy]"
}

if ($startServers) {
    Write-Host ""
    Write-Host "Starting development servers..." -ForegroundColor Cyan
    Write-Host ""
    
    # Start backend in new window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; uv run python main.py" -WindowStyle Normal
    
    # Wait for backend to start
    Start-Sleep -Seconds 3
    
    # Start frontend in new window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WindowStyle Normal
    
    # Open browser
    Start-Sleep -Seconds 5
    Start-Process "http://localhost:3000"
    
    Write-Host "✓ Both servers are starting in separate windows..." -ForegroundColor Green
    Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Gray
    Write-Host "  Backend:  http://localhost:5000" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Setup script completed!" -ForegroundColor Green
if (-not $AutoStart) {
    Read-Host "Press Enter to exit"
}
