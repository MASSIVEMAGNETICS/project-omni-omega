#!/bin/bash
# =====================================================================
# OmniLoader Studio - One-Click Install Script (Mac/Linux)
# =====================================================================
set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}OmniLoader Studio - Install${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check Python 3
echo -e "${BLUE}[1/4] Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Please install Python 3.8+ from:"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Check Python version >= 3.8
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}ERROR: Python 3.8+ is required (found ${PYTHON_VERSION})${NC}"
    exit 1
fi

# Check pip
if ! python3 -m pip --version &> /dev/null; then
    echo -e "${RED}ERROR: pip is not installed${NC}"
    echo "Please install pip for Python 3"
    exit 1
fi
echo -e "${GREEN}✓ pip is available${NC}"
echo ""

# Create virtual environment
echo -e "${BLUE}[2/4] Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip --quiet
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install dependencies
echo -e "${BLUE}[3/4] Installing dependencies...${NC}"
echo "This may take 5-15 minutes depending on your connection..."
python -m pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}ERROR: Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Validate installation
echo -e "${BLUE}[4/4] Validating installation...${NC}"
if [ -f "validate_install.py" ]; then
    python validate_install.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Installation validated${NC}"
    else
        echo -e "${YELLOW}Warning: Validation had issues, but installation completed${NC}"
    fi
else
    echo -e "${YELLOW}Skipping validation (validate_install.py not found)${NC}"
fi
echo ""

# Success message
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Run the app: ./scripts/run.sh"
echo "  2. Or use VS Code: Run Task → ⚡ Run (One Click)"
echo "  3. Access UI at: http://localhost:8501"
echo ""
echo -e "${GREEN}Ready to run OmniLoader Studio!${NC}"
