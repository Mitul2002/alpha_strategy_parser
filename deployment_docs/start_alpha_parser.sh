#!/bin/bash

# =============================================================================
# Alpha Strategy Parser - Unified Startup Script
# =============================================================================
# This script starts both the FastAPI backend and Vue.js frontend
# with proper path handling and error checking
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}=============================================================================${NC}"
    echo -e "${PURPLE}🚀 Alpha Strategy Parser - Starting System${NC}"
    echo -e "${PURPLE}=============================================================================${NC}"
}

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null && print_success "Backend stopped" || print_warning "Backend was not running"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null && print_success "Frontend stopped" || print_warning "Frontend was not running"
    fi
    
    # Kill any remaining processes with timeout
    timeout 2 pkill -f "python.*app.py" 2>/dev/null || true
    timeout 2 pkill -f "vite" 2>/dev/null || true
    
    echo -e "${GREEN}👋 Goodbye!${NC}"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Print header
print_header

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

print_status "Script directory: $SCRIPT_DIR"
print_status "Project root: $PROJECT_ROOT"

# Change to project root
cd "$PROJECT_ROOT"

# Verify we're in the right directory
if [ ! -f "webapi/app.py" ]; then
    print_error "Backend app.py not found. Expected: $PROJECT_ROOT/webapi/app.py"
    print_error "Please run this script from the alpha_strategy_parser directory"
    exit 1
fi

if [ ! -d "alpha-strategy-frontend" ]; then
    print_error "Frontend directory not found. Expected: $PROJECT_ROOT/alpha-strategy-frontend"
    exit 1
fi

print_success "Directory structure verified"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found at: $PROJECT_ROOT/venv"
    print_error "Please create it first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

print_success "Virtual environment found"

# Check if frontend dependencies are installed
if [ ! -d "alpha-strategy-frontend/node_modules" ]; then
    print_error "Frontend dependencies not installed"
    print_error "Please install them first:"
    echo "  cd alpha-strategy-frontend"
    echo "  npm install"
    exit 1
fi

print_success "Frontend dependencies found"

# Kill any existing processes with timeout to avoid hanging
print_status "Cleaning up existing processes..."
timeout 3 pkill -f "python.*app.py" 2>/dev/null || true
timeout 3 pkill -f "vite" 2>/dev/null || true
sleep 1

# Start FastAPI backend
print_status "Starting FastAPI backend..."
cd "$PROJECT_ROOT/webapi"

# Activate virtual environment and start backend
source ../venv/bin/activate
export PYTHONPATH="$PROJECT_ROOT"

# Start backend in background
python app.py > ../backend.log 2>&1 &
BACKEND_PID=$!

print_success "Backend started with PID: $BACKEND_PID"

# Wait for backend to start
print_status "Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "Backend failed to start. Check backend.log for details:"
    cat ../backend.log
    exit 1
fi

# Test backend connection
print_status "Testing backend connection..."
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    print_success "Backend is responding"
else
    print_warning "Backend health check failed, but continuing..."
fi

# Start Vue.js frontend
print_status "Starting Vue.js frontend..."
cd "$PROJECT_ROOT/alpha-strategy-frontend"

# Start frontend in background
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

print_success "Frontend started with PID: $FRONTEND_PID"

# Wait for frontend to start
print_status "Waiting for frontend to initialize..."
sleep 8

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    print_error "Frontend failed to start. Check frontend.log for details:"
    cat ../frontend.log
    cleanup
    exit 1
fi

# Final status
echo -e "\n${GREEN}=============================================================================${NC}"
echo -e "${GREEN}✅ Alpha Strategy Parser System Started Successfully!${NC}"
echo -e "${GREEN}=============================================================================${NC}"
echo -e "${CYAN}🔧 Backend API:${NC} http://127.0.0.1:8000"
echo -e "${CYAN}🎯 Frontend UI:${NC} http://localhost:5173"
echo -e "${CYAN}📊 API Docs:${NC} http://127.0.0.1:8000/docs"
echo -e "${CYAN}📋 Health Check:${NC} http://127.0.0.1:8000/health"
echo -e "${GREEN}=============================================================================${NC}"
echo -e "${YELLOW}📝 Logs:${NC}"
echo -e "   Backend:  $PROJECT_ROOT/backend.log"
echo -e "   Frontend: $PROJECT_ROOT/frontend.log"
echo -e "${GREEN}=============================================================================${NC}"
echo -e "${PURPLE}Press Ctrl+C to stop all services${NC}"

# Wait for user to stop
wait
