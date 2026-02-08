@echo off
REM ============================================================================
REM ChannelSmith Executable Builder for Windows
REM
REM This script builds a standalone .exe executable for Windows 10+
REM
REM Usage: build_exe.bat
REM Output: dist/ChannelSmith.exe (~50MB)
REM ============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║            ChannelSmith Executable Builder (Windows)                   ║
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

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
echo.

REM Check if venv exists
if not exist venv\ (
    echo [INFO] Virtual environment not found
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo.
    echo Try running manually:
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller is not installed
    echo Installing PyInstaller...
    pip install -q pyinstaller>=5.13.0
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
)
echo [OK] PyInstaller available
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist dist\ rmdir /s /q dist >nul 2>&1
if exist build\ rmdir /s /q build >nul 2>&1
if exist *.spec del /q *.spec >nul 2>&1
echo [OK] Old build files removed
echo.

REM Build executable
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                    Building ChannelSmith.exe                           ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.
echo This may take 2-5 minutes, please wait...
echo.

pyinstaller channelsmith.spec --clean
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to build executable
    echo.
    echo Try debugging with:
    echo   pyinstaller channelsmith.spec -y
    echo.
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                    Build Successful!                                   ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

REM Check if executable exists
if exist dist\ChannelSmith.exe (
    for /f "%%A in ('dir /b dist\ChannelSmith.exe') do set /a SIZE=%%~zA"
    set /a SIZE_MB=!SIZE! / 1048576
    echo [OK] Executable created: dist\ChannelSmith.exe (!SIZE_MB! MB)
) else (
    echo [WARNING] Executable not found at expected location
)

echo.
echo Next steps:
echo   1. Test the executable:
echo      dist\ChannelSmith.exe
echo.
echo   2. If successful, create a release archive:
echo      mkdir ChannelSmith-Windows
echo      copy dist\ChannelSmith.exe ChannelSmith-Windows\
echo      copy CHANGELOG.md ChannelSmith-Windows\
echo      copy README.md ChannelSmith-Windows\
echo      7z a ChannelSmith-Windows.zip ChannelSmith-Windows\
echo.
echo   3. Upload to GitHub Releases
echo.
pause
