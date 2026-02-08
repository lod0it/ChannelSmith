#!/bin/bash
################################################################################
# ChannelSmith Executable Builder for macOS and Linux
#
# This script builds a standalone executable for macOS and Linux systems.
#
# Usage: ./build_exe.sh
# Output: dist/ChannelSmith (~50MB)
#
# Note: Make executable first with: chmod +x build_exe.sh
################################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}        ChannelSmith Executable Builder (macOS/Linux)                   ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════╝${NC}\n"
}

print_ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_step() {
    echo -e "\n${BLUE}==>${NC} $1"
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Main execution
print_header

# Check Python installation
print_step "Checking Python installation"
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    echo ""
    echo "Installation instructions:"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt-get install python3 python3-venv python3-pip"
    echo ""
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_ok "Python $PYTHON_VERSION found"
echo ""

# Setup or activate virtual environment
print_step "Setting up virtual environment"
if [ -d "venv" ]; then
    print_ok "Virtual environment found"
else
    print_info "Creating new virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    print_ok "Virtual environment created"
fi

echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi
print_ok "Virtual environment activated"
echo ""

# Install dependencies
print_step "Installing dependencies"
echo "Installing from requirements.txt..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies"
    echo "Try running: pip install -r requirements.txt"
    exit 1
fi
print_ok "Dependencies installed"
echo ""

# Verify PyInstaller
print_step "Checking PyInstaller"
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    print_info "PyInstaller not found, installing..."
    pip install -q pyinstaller>=5.13.0
    if [ $? -ne 0 ]; then
        print_error "Failed to install PyInstaller"
        exit 1
    fi
fi
print_ok "PyInstaller available"
echo ""

# Clean previous builds
print_step "Cleaning previous builds"
rm -rf dist build __pycache__ *.spec .spec 2>/dev/null
print_ok "Old build files removed"
echo ""

# Build executable
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}                   Building ChannelSmith Executable                      ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════╝${NC}\n"

echo "This may take 2-5 minutes, please wait..."
echo ""

python3 -m PyInstaller channelsmith.spec --clean
if [ $? -ne 0 ]; then
    echo ""
    print_error "Failed to build executable"
    echo ""
    echo "Try debugging with:"
    echo "  python3 -m PyInstaller channelsmith.spec -y"
    echo ""
    exit 1
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}                   Build Successful!                                   ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════╝${NC}\n"

# Check if executable exists and show size
if [ -f "dist/ChannelSmith" ]; then
    SIZE=$(du -h dist/ChannelSmith | cut -f1)
    print_ok "Executable created: dist/ChannelSmith ($SIZE)"
else
    echo -e "${YELLOW}[WARNING]${NC} Executable not found at expected location"
fi

echo ""
echo "Next steps:"
echo "  1. Test the executable:"
echo "     ./dist/ChannelSmith"
echo ""
echo "  2. If successful, create a release archive:"
echo "     mkdir -p ChannelSmith-$(uname -s)"
echo "     cp dist/ChannelSmith ChannelSmith-$(uname -s)/"
echo "     cp CHANGELOG.md ChannelSmith-$(uname -s)/"
echo "     cp README.md ChannelSmith-$(uname -s)/"
echo "     tar czf ChannelSmith-$(uname -s).tar.gz ChannelSmith-$(uname -s)/"
echo ""
echo "  3. Upload to GitHub Releases"
echo ""
