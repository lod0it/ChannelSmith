@echo off
REM ============================================================================
REM ChannelSmith Launcher - TexturePacker.bat
REM
REM Purpose: Launch ChannelSmith texture packing application
REM Version: 0.1.0-beta
REM
REM Usage: Double-click this file or run from command prompt
REM        No arguments needed - application will launch with GUI
REM ============================================================================

setlocal enabledelayedexpansion

REM Set window title
title ChannelSmith Texture Packer

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Remove trailing backslash if present
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

echo.
echo ============================================================================
echo  ChannelSmith - Texture Channel Packing Tool v0.1.0-beta
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Get Python version for display
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Found: %PYTHON_VERSION%
echo.

REM Check if we're in a virtual environment
if defined VIRTUAL_ENV (
    echo [INFO] Virtual environment active: %VIRTUAL_ENV%
) else (
    REM Try to activate venv if it exists
    if exist "%SCRIPT_DIR%\venv\Scripts\activate.bat" (
        echo [INFO] Activating virtual environment...
        call "%SCRIPT_DIR%\venv\Scripts\activate.bat"
    ) else (
        echo [WARNING] No virtual environment found
        echo [INFO] Make sure to install dependencies: pip install -r requirements.txt
    )
)

echo.

REM Check if required packages are installed
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Required packages not found
    echo.
    echo Please install dependencies with:
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [INFO] Starting ChannelSmith application...
echo.

REM Launch the application
python -m channelsmith

REM Capture exit code
set EXIT_CODE=%errorlevel%

if %EXIT_CODE% equ 0 (
    echo.
    echo [INFO] ChannelSmith closed normally
    exit /b 0
) else (
    echo.
    echo [ERROR] ChannelSmith exited with error code: %EXIT_CODE%
    echo.
    echo Please check the error messages above or contact support
    echo.
    pause
    exit /b %EXIT_CODE%
)
