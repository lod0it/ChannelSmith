@echo off
REM ============================================================================
REM ChannelSmith Web UI Launcher
REM
REM This script launches the ChannelSmith web UI with automatic dependency
REM installation and browser opening.
REM
REM Usage: Double-click this file or run from command prompt
REM ============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                   ChannelSmith Web UI Launcher                         ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo.

REM Check if virtual environment exists
if exist venv\ (
    echo [OK] Virtual environment found
    echo.
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo [ERROR] Failed to activate virtual environment
        pause
        exit /b 1
    )
) else (
    echo [INFO] Virtual environment not found
    echo.
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    echo.
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo [OK] Virtual environment activated
echo.

REM Install/upgrade dependencies
echo Installing dependencies from requirements.txt...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies
    echo.
    echo Try running this command manually in PowerShell/CMD:
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Flask is not installed properly
    echo Please run: pip install flask flask-cors
    echo.
    pause
    exit /b 1
)
echo [OK] Flask is available
echo.

REM Launch the web UI
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                     Launching ChannelSmith Web UI                      ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo Opening http://localhost:5000 in your browser...
echo.
echo Press Ctrl+C to stop the server
echo.

REM Check if port 5000 is available
netstat -ano | findstr ":5000" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 5000 might already be in use
    echo.
)

REM Launch Flask app
python -m channelsmith

REM Handle exit
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to launch ChannelSmith
    echo.
    pause
) else (
    echo.
    echo [OK] ChannelSmith closed normally
    echo.
)

endlocal
