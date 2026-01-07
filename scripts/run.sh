#!/bin/bash
# =====================================================================
# OmniLoader Studio - One-Click Run Script (Mac/Linux)
# =====================================================================
set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-8501}

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}OmniLoader Studio - Run${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}ERROR: Virtual environment not found${NC}"
    echo "Please run the install script first:"
    echo "  ./scripts/install.sh"
    exit 1
fi

# Activate virtual environment
echo -e "${CYAN}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if dependencies are installed
echo -e "${CYAN}Checking dependencies...${NC}"
if ! python -c "import fastapi, streamlit" 2>/dev/null; then
    echo -e "${RED}ERROR: Dependencies not installed${NC}"
    echo "Please run the install script first:"
    echo "  ./scripts/install.sh"
    exit 1
fi
echo -e "${GREEN}✓ Dependencies OK${NC}"
echo ""

# Check if ports are available
echo -e "${CYAN}Checking ports...${NC}"
if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Port $BACKEND_PORT is already in use${NC}"
    echo "Backend may already be running or another service is using the port."
fi

if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Port $FRONTEND_PORT is already in use${NC}"
    echo "Frontend may already be running or another service is using the port."
fi
echo ""

# Create cleanup handler
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down OmniLoader Studio...${NC}"
    
    # Kill backend and frontend
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Also kill by port as backup
    lsof -ti:$BACKEND_PORT 2>/dev/null | while read pid; do kill "$pid" 2>/dev/null || true; done
    lsof -ti:$FRONTEND_PORT 2>/dev/null | while read pid; do kill "$pid" 2>/dev/null || true; done
    
    echo -e "${GREEN}Shutdown complete${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start services
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Starting OmniLoader Studio...${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${GREEN}Backend API:${NC}  http://localhost:$BACKEND_PORT"
echo -e "${GREEN}API Docs:${NC}     http://localhost:$BACKEND_PORT/docs"
echo -e "${GREEN}Studio UI:${NC}    http://localhost:$FRONTEND_PORT"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Start backend
echo -e "${CYAN}Starting backend...${NC}"
uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo -e "${CYAN}Waiting for backend...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}ERROR: Backend failed to start${NC}"
        exit 1
    fi
    sleep 1
done
echo ""

# Start frontend
echo -e "${CYAN}Starting Studio UI...${NC}"
streamlit run ui/app.py --server.port $FRONTEND_PORT --server.address 0.0.0.0 --server.headless true &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Studio UI started (PID: $FRONTEND_PID)${NC}"
echo ""

# Wait a moment for frontend to start
sleep 3

# Open browser (platform-specific)
echo -e "${CYAN}Opening browser...${NC}"
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:$FRONTEND_PORT" 2>/dev/null &
elif command -v open &> /dev/null; then
    open "http://localhost:$FRONTEND_PORT" 2>/dev/null &
fi
echo ""

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}OmniLoader Studio is running!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Access at:"
echo "  • Studio UI: http://localhost:$FRONTEND_PORT"
echo "  • API Docs:  http://localhost:$BACKEND_PORT/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Keep script running
wait
