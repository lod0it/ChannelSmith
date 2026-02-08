@echo off
REM ============================================================================
REM ChannelSmith Test Runner
REM
REM This script runs the test suite and shows results
REM
REM Usage: Double-click this file or run from command prompt
REM ============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║                     ChannelSmith Test Runner                           ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

REM Check if virtual environment exists
if not exist venv\ (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt >nul 2>&1

echo.
echo Running tests...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Show menu if no argument
if "%1"=="" (
    echo Available test options:
    echo.
    echo   1. Run ALL tests (Core + API)
    echo   2. Run API tests only (22 tests)
    echo   3. Run Core tests only (207 tests)
    echo   4. Run with coverage report
    echo   5. Run verbose output
    echo   6. Exit
    echo.
    set /p choice="Select option (1-6): "
) else (
    set choice=%1
)

if "!choice!"=="1" (
    echo Running ALL tests...
    echo.
    pytest tests/test_api/ tests/test_core/ -q
    goto :end
)

if "!choice!"=="2" (
    echo Running API tests...
    echo.
    pytest tests/test_api/ -v
    goto :end
)

if "!choice!"=="3" (
    echo Running Core tests...
    echo.
    pytest tests/test_core/ -q
    goto :end
)

if "!choice!"=="4" (
    echo Running tests with coverage...
    echo.
    pytest tests/ --cov=channelsmith --cov-report=html
    echo.
    echo Coverage report generated: htmlcov\index.html
    goto :end
)

if "!choice!"=="5" (
    echo Running tests with verbose output...
    echo.
    pytest tests/ -v
    goto :end
)

if "!choice!"=="6" (
    exit /b 0
)

echo Invalid option
goto :end

:end
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause

endlocal
