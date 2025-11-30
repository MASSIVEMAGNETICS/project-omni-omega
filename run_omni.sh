#!/bin/bash
# =====================================================================
# OmniLoader Studio - Cross-Platform Launcher (Linux/macOS/Web)
# Production-grade local-first AI model manager
# =====================================================================

set -e

# Configuration
BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-8501}
VENV_DIR=${VENV_DIR:-venv}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Header
print_header() {
    echo -e "${MAGENTA}"
    echo "========================================================"
    echo " ___  __  __ _   _ ___ _     ___    _    ____  _____ ____  "
    echo "/ _ \|  \/  | \ | |_ _| |   / _ \  / \  |  _ \| ____|  _ \ "
    echo "| | | | |\/| |  \| || || |  | | | |/ _ \ | | | |  _| | |_) |"
    echo "| |_| | |  | | |\  || || |__| |_| / ___ \| |_| | |___|  _ < "
    echo " \___/|_|  |_|_| \_|___|_____\___/_/   \_\____/|_____|_| \_\\"
    echo ""
    echo " Production-grade local-first AI model manager"
    echo "========================================================"
    echo -e "${NC}"
}

# Check command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}ERROR: $1 is not installed${NC}"
        return 1
    fi
    return 0
}

# Check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    fi
    return 1  # Port is free
}

# Wait for service to be ready
wait_for_service() {
    local url=$1
    local max_attempts=${2:-30}
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    return 1
}

# Setup function
setup() {
    echo -e "${CYAN}[1/5] Checking Python installation...${NC}"
    if ! check_command python3; then
        echo -e "${RED}Please install Python 3.8+ first${NC}"
        exit 1
    fi
    PYVER=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo -e "   ${GREEN}Python $PYVER found${NC}"
    
    echo -e "\n${CYAN}[2/5] Setting up virtual environment...${NC}"
    if [ ! -d "$VENV_DIR" ]; then
        echo "   Creating new virtual environment..."
        python3 -m venv "$VENV_DIR"
        echo -e "   ${GREEN}Virtual environment created${NC}"
    else
        echo "   Using existing virtual environment"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    echo -e "\n${CYAN}[3/5] Checking dependencies...${NC}"
    if ! pip show fastapi >/dev/null 2>&1; then
        echo "   Installing dependencies (this may take a few minutes)..."
        pip install -q -r requirements.txt
    else
        echo "   Dependencies already installed"
    fi
    
    echo -e "\n${CYAN}[4/5] Checking for running instances...${NC}"
    if check_port $BACKEND_PORT; then
        echo -e "   ${YELLOW}WARNING: Port $BACKEND_PORT is already in use${NC}"
        read -p "   Continue anyway? (y/n): " CONTINUE
        if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
            exit 0
        fi
    else
        echo "   Ports are available"
    fi
}

# Start services
start_services() {
    echo -e "\n${CYAN}[5/5] Launching OmniLoader Studio...${NC}"
    echo ""
    echo "========================================================"
    echo -e " Starting services:"
    echo -e "   ${GREEN}Backend API:${NC}  http://localhost:$BACKEND_PORT"
    echo -e "   ${GREEN}API Docs:${NC}     http://localhost:$BACKEND_PORT/docs"
    echo -e "   ${GREEN}Studio UI:${NC}    http://localhost:$FRONTEND_PORT"
    echo "========================================================"
    echo ""
    
    # Start backend in background
    echo "Starting backend..."
    source "$VENV_DIR/bin/activate"
    uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    
    # Wait for backend
    echo "Waiting for backend to be ready..."
    if wait_for_service "http://localhost:$BACKEND_PORT/health" 30; then
        echo -e "${GREEN}Backend is ready!${NC}"
    else
        echo -e "${YELLOW}WARNING: Backend may not have started correctly${NC}"
    fi
    
    # Start frontend
    echo ""
    echo "Starting Studio UI..."
    streamlit run ui/app.py --server.port $FRONTEND_PORT --server.address 0.0.0.0 --server.headless true &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    
    # Wait for frontend
    sleep 3
    
    # Open browser (platform-specific)
    echo ""
    echo "Opening browser..."
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:$FRONTEND_PORT" 2>/dev/null &
    elif command -v open &> /dev/null; then
        open "http://localhost:$FRONTEND_PORT" 2>/dev/null &
    fi
    
    # Save PIDs for later
    echo "$BACKEND_PID" > .omniloader_backend.pid
    echo "$FRONTEND_PID" > .omniloader_frontend.pid
    
    echo ""
    echo "========================================================"
    echo -e " ${GREEN}OmniLoader Studio is running!${NC}"
    echo ""
    echo " To stop services, press Ctrl+C or run:"
    echo "   ./run_omni.sh stop"
    echo "========================================================"
    
    # Wait for user interrupt
    trap cleanup SIGINT SIGTERM
    wait
}

# Stop services
stop_services() {
    echo "Stopping OmniLoader services..."
    
    if [ -f .omniloader_backend.pid ]; then
        BACKEND_PID=$(cat .omniloader_backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            echo "Backend stopped"
        fi
        rm -f .omniloader_backend.pid
    fi
    
    if [ -f .omniloader_frontend.pid ]; then
        FRONTEND_PID=$(cat .omniloader_frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            echo "Frontend stopped"
        fi
        rm -f .omniloader_frontend.pid
    fi
    
    # Also try to kill by port
    lsof -ti:$BACKEND_PORT | xargs -r kill 2>/dev/null || true
    lsof -ti:$FRONTEND_PORT | xargs -r kill 2>/dev/null || true
    
    echo -e "${GREEN}Services stopped${NC}"
}

# Cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    stop_services
    exit 0
}

# Status check
status() {
    echo "OmniLoader Service Status"
    echo "========================="
    echo ""
    
    if check_port $BACKEND_PORT; then
        echo -e "Backend (port $BACKEND_PORT): ${GREEN}RUNNING${NC}"
        if curl -s "http://localhost:$BACKEND_PORT/health" | grep -q "healthy"; then
            echo -e "  Health: ${GREEN}HEALTHY${NC}"
        else
            echo -e "  Health: ${YELLOW}UNKNOWN${NC}"
        fi
    else
        echo -e "Backend (port $BACKEND_PORT): ${RED}NOT RUNNING${NC}"
    fi
    
    echo ""
    
    if check_port $FRONTEND_PORT; then
        echo -e "Frontend (port $FRONTEND_PORT): ${GREEN}RUNNING${NC}"
    else
        echo -e "Frontend (port $FRONTEND_PORT): ${RED}NOT RUNNING${NC}"
    fi
}

# Run tests
run_tests() {
    echo "Running tests..."
    source "$VENV_DIR/bin/activate"
    pytest tests/ -v
}

# Print usage
usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start   - Start OmniLoader Studio (default)"
    echo "  stop    - Stop all services"
    echo "  status  - Check service status"
    echo "  test    - Run tests"
    echo "  help    - Show this help message"
}

# Main
print_header

case "${1:-start}" in
    start)
        setup
        start_services
        ;;
    stop)
        stop_services
        ;;
    status)
        status
        ;;
    test)
        setup
        run_tests
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        usage
        exit 1
        ;;
esac
