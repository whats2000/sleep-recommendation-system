# Symphony AI Sleep Recommendation System - Setup Guide

This guide explains how to use the automated setup scripts to get the project running quickly.

## Quick Start

### Option 1: Simple Launcher (Recommended)
Double-click `start.bat` and choose your preferred setup method from the menu.

### Option 2: Direct Script Execution

#### PowerShell Setup (Recommended)
```powershell
# Run with automatic installation
.\setup.ps1

# Run with auto-start (no prompts)
.\setup.ps1 -AutoStart

# Skip specific installations
.\setup.ps1 -SkipNodeInstall -SkipUvInstall
```

#### Batch Setup (Basic)
```cmd
setup.bat
```

## What the Scripts Do

### Automatic Installation
- **Node.js**: Installs via winget, chocolatey, or prompts for manual installation
- **uv**: Installs via official PowerShell script or pip
- **Dependencies**: Sets up both Python and Node.js project dependencies

### Project Setup
1. Creates Python virtual environment in `backend/`
2. Installs Python dependencies using `uv sync`
3. Installs Node.js dependencies using `npm install`
4. Optionally starts both development servers

### Development Servers
- **Backend**: Flask server on `http://localhost:5000`
- **Frontend**: Vite dev server on `http://localhost:3000`

## Prerequisites

### Automatic Installation (PowerShell)
- Windows 10/11 with PowerShell 5.1+
- Internet connection
- Optional: Administrator privileges for system-wide installations

### Manual Installation Required
If automatic installation fails, install manually:

1. **Node.js**: Download from [nodejs.org](https://nodejs.org/)
2. **uv**: Follow instructions at [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)

## Script Features

### PowerShell Script (`setup.ps1`)
- ✅ Automatic Node.js installation via winget/chocolatey
- ✅ Automatic uv installation
- ✅ Administrator privilege detection
- ✅ Colored output and progress indicators
- ✅ Error handling and recovery
- ✅ Command-line parameters
- ✅ Environment variable refresh

### Batch Script (`setup.bat`)
- ✅ Basic dependency checking
- ✅ Manual installation prompts
- ✅ Cross-platform compatibility
- ⚠️ Limited automatic installation capabilities

## Troubleshooting

### Common Issues

#### "uv not found" after installation
- Restart your terminal/command prompt
- Or run: `refreshenv` (if available)
- Or manually add uv to your PATH

#### Permission errors during installation
- Run PowerShell as Administrator
- Or install dependencies manually

#### Node.js installation fails
- Download and install manually from [nodejs.org](https://nodejs.org/)
- Ensure you select "Add to PATH" during installation

#### Python dependencies fail to install
- Ensure you have Python 3.11+ installed
- Check your internet connection
- Try running: `cd backend && uv sync --verbose`

### Manual Setup (Fallback)

If scripts fail, set up manually:

```bash
# Backend setup
cd backend
python -m pip install uv
uv venv
uv sync

# Frontend setup
cd ../frontend
npm install

# Start servers (in separate terminals)
cd backend && uv run python main.py
cd frontend && npm run dev
```

## Environment Variables

The project requires certain environment variables. Create a `.env` file in the `backend/` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
FLASK_HOST=localhost
FLASK_PORT=5000
FLASK_DEBUG=true
```

## Development Workflow

After initial setup:

1. **Start development**: Run `start.bat` → Option 3 (Quick start)
2. **Backend only**: `cd backend && uv run python main.py`
3. **Frontend only**: `cd frontend && npm run dev`
4. **Run tests**: `cd backend && uv run python run_tests.py`

## Script Parameters

### PowerShell Parameters
- `-AutoStart`: Start servers automatically without prompts
- `-SkipNodeInstall`: Skip Node.js installation check
- `-SkipUvInstall`: Skip uv installation check

Example:
```powershell
.\setup.ps1 -AutoStart -SkipNodeInstall
```

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure you have the latest versions of Node.js and Python
3. Try running scripts as Administrator
4. For persistent issues, set up the project manually using the fallback instructions
