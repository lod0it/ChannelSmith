#!/bin/bash
################################################################################
# ChannelSmith First-Time Setup Script
#
# This script performs a complete first-time setup for ChannelSmith:
# - Checks Python installation
# - Creates virtual environment
# - Installs all dependencies
# - Runs health check
# - Prints success message with instructions
#
# Usage: ./install.sh
# Note: Make executable first with: chmod +x install.sh
################################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function for colored output
print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}                     ChannelSmith Setup Wizard                          ${BLUE}║${NC}"
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
    echo -e "\n${BLUE}=>${NC} $1"
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Start setup
print_header

# Step 1: Check Python installation
print_step "Checking Python installation"
if ! command -v python3 &> /dev/null; then
    echo ""
    print_error "Python 3 is not installed or not in PATH"
    echo ""
    echo "Installation instructions:"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt-get install python3 python3-venv python3-pip"
    echo "  Windows: https://www.python.org/ (use launch_web_ui.bat instead)"
    echo ""
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_ok "Python $PYTHON_VERSION found"

# Step 2: Create virtual environment
print_step "Setting up virtual environment"
if [ -d "venv" ]; then
    print_ok "Virtual environment already exists"
else
    print_info "Creating new virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    print_ok "Virtual environment created"
fi

# Step 3: Activate virtual environment
print_step "Activating virtual environment"
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi
print_ok "Virtual environment activated"

# Step 4: Upgrade pip
print_step "Upgrading pip"
pip install --upgrade pip -q
if [ $? -ne 0 ]; then
    print_error "Failed to upgrade pip"
    exit 1
fi
print_ok "pip upgraded"

# Step 5: Install dependencies
print_step "Installing dependencies"
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies"
    echo "Try running: pip install -r requirements.txt"
    exit 1
fi
print_ok "All dependencies installed"

# Step 6: Verify Flask installation
print_step "Verifying Flask installation"
python3 -c "import flask; import flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    print_error "Flask or flask-cors is not installed properly"
    echo "Try running: pip install flask flask-cors"
    exit 1
fi
print_ok "Flask and dependencies verified"

# Step 7: Run health check
print_step "Running health check"
python3 -c "
import sys
try:
    from channelsmith.core.packing_engine import pack_texture_from_template
    from channelsmith.templates.template_loader import load_template
    from PIL import Image
    import numpy as np

    # Test basic packing
    template = load_template('channelsmith/templates/orm.json')

    # Create dummy test images
    test_img = Image.new('L', (128, 128), 128)
    textures = {
        'ambient_occlusion': test_img,
        'roughness': test_img,
        'metallic': test_img
    }

    result = pack_texture_from_template(textures, template)
    print('SUCCESS: Core packing engine works')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
" 2>/dev/null

if [ $? -ne 0 ]; then
    print_error "Health check failed - core functionality may be broken"
    exit 1
fi
print_ok "Health check passed - core functionality working"

# Success message
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}                      ${GREEN}✓ Setup Complete!${NC}                                    ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════╝${NC}\n"

echo "ChannelSmith is now ready to use!"
echo ""
echo "To launch the web UI, run:"
echo -e "  ${GREEN}./launch_web_ui.sh${NC}"
echo ""
echo "Or for a quick start:"
echo -e "  ${GREEN}./launch_simple.sh${NC}"
echo ""
echo "For manual activation in the future:"
echo -e "  ${GREEN}source venv/bin/activate${NC}"
echo "  ${GREEN}python -m channelsmith${NC}"
echo ""
