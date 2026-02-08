#!/bin/bash
# ChannelSmith Web UI - Quick Start (Simplified Version)
# Usage: ./launch_simple.sh (or double-click on macOS)

cd "$(dirname "$0")"

echo "Starting ChannelSmith Web UI..."
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "Launching..."
python3 -m channelsmith
