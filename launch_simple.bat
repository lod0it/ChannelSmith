@echo off
REM ChannelSmith Web UI - Quick Start (Simplified Version)
REM Double-click to launch the web UI
REM Browser opens automatically at http://localhost:5000

cd /d "%~dp0"

echo Starting ChannelSmith Web UI...
echo.
echo Installing dependencies...
pip install -q -r requirements.txt

echo Launching...
python -m channelsmith

pause
