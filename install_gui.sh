#!/bin/bash
# =====================================================================
# OmniLoader Studio - GUI Installer Launcher for Mac/Linux
# Production-grade local-first AI model manager
# =====================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "OmniLoader Studio - GUI Installer"
echo "=================================="

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Please install Python 3.8+ from:"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt install python3 python3-tk"
    exit 1
fi

# Check for tkinter
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: tkinter is not available${NC}"
    echo "Please install tkinter:"
    echo "  Ubuntu/Debian: sudo apt install python3-tk"
    echo "  Fedora: sudo dnf install python3-tkinter"
    echo "  macOS: tkinter is included with Python from python.org"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Launch GUI Installer
echo -e "${GREEN}Launching GUI Installer...${NC}"
python3 "$SCRIPT_DIR/install_gui.py"
