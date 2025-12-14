@echo off
REM 97%+ AI Medical Coding Assistant - Auto Startup Script

setlocal enabledelayedexpansion

echo.
echo ========================================================================
echo   97-PERCENT AI-POWERED MEDICAL CODING ASSISTANT - AUTO START
echo ========================================================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo [*] Project Directory: %CD%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

echo [*] Checking dependencies...
python -c "import uvicorn, sentence_transformers, sklearn" >nul 2>&1
if errorlevel 1 (
    echo [!] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)
echo [OK] All dependencies ready
echo.

echo [*] Starting AI Medical Coding Server...
echo     This will take 3-5 minutes on first run
echo     (Downloading and computing AI embeddings)
echo.

REM Start the server
python -m uvicorn api.main:app --reload

pause
