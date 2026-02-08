#!/bin/bash
################################################################################
# ChannelSmith Web UI Launcher
#
# This script launches the ChannelSmith web UI with automatic dependency
# installation and browser opening.
#
# Usage: ./launch_web_ui.sh (or double-click if on macOS)
# Note: Make executable first with: chmod +x launch_web_ui.sh
################################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Helper function for colored output
print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}                   ChannelSmith Web UI Launcher                         ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════╝${NC}\n"
}

print_ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Main execution
print_header

# Check if Python3 is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo ""
    print_error "Python 3 is not installed or not in PATH"
    echo ""
    echo "Please install Python 3.8+ from https://www.python.org/"
    echo "On macOS: brew install python3"
    echo "On Linux: sudo apt-get install python3 python3-venv python3-pip"
    echo ""
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_ok "Python $PYTHON_VERSION found"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    print_ok "Virtual environment found"
    echo ""
    echo "Activating virtual environment..."
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        print_error "Failed to activate virtual environment"
        exit 1
    fi
else
    print_info "Virtual environment not found"
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    print_ok "Virtual environment created"
    echo ""
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

print_ok "Virtual environment activated"
echo ""

# Install/upgrade dependencies
echo "Installing dependencies from requirements.txt..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    print_error "Failed to install dependencies"
    echo ""
    echo "Try running this command manually:"
    echo "  pip install -r requirements.txt"
    echo ""
    exit 1
fi
print_ok "Dependencies installed"
echo ""

# Check if Flask is installed
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    print_error "Flask is not installed properly"
    echo "Please run: pip install flask flask-cors"
    echo ""
    exit 1
fi
print_ok "Flask is available"
echo ""

# Check if port 5000 is available (try different methods)
PORT_IN_USE=0
if command -v lsof &> /dev/null; then
    lsof -i :5000 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        PORT_IN_USE=1
    fi
elif command -v ss &> /dev/null; then
    ss -ltn | grep -q ":5000 "
    if [ $? -eq 0 ]; then
        PORT_IN_USE=1
    fi
fi

if [ $PORT_IN_USE -eq 1 ]; then
    print_warning "Port 5000 might already be in use"
    echo ""
fi

# Launch the web UI
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}                     Launching ChannelSmith Web UI                      ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════╝${NC}\n"

echo "Opening http://localhost:5000 in your browser..."
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Open browser based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "http://localhost:5000" 2>/dev/null &
elif command -v xdg-open &> /dev/null; then
    # Linux with xdg-open
    xdg-open "http://localhost:5000" 2>/dev/null &
fi

# Launch Flask app
python3 -m channelsmith

# Handle exit
if [ $? -eq 0 ]; then
    echo ""
    print_ok "ChannelSmith closed normally"
    echo ""
else
    echo ""
    print_error "Failed to launch ChannelSmith"
    echo ""
    read -p "Press Enter to exit..."
fi
