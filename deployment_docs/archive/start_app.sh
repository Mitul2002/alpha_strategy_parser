#!/bin/bash

# Alpha Strategy Parser - Startup Script
# This script starts both the FastAPI backend and Vue.js frontend

echo "🚀 Starting Alpha Strategy Parser..."
echo "=================================="

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n🛑 Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend stopped"
    fi
    echo "👋 Goodbye!"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Check if we're in the right directory
if [ ! -f "webapi/app.py" ]; then
    echo "❌ Error: Please run this script from the alpha_strategy_parser directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected: alpha_strategy_parser/"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "alpha-strategy-frontend/node_modules" ]; then
    echo "❌ Error: Frontend dependencies not installed. Please run:"
    echo "   cd alpha-strategy-frontend"
    echo "   npm install"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating Python virtual environment..."
source venv/bin/activate

# Start FastAPI backend
echo "🌐 Starting FastAPI backend..."
cd webapi
python app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if ! curl -s http://127.0.0.1:8000 > /dev/null; then
    echo "❌ Backend failed to start"
    cleanup
    exit 1
fi
echo "✅ Backend running on http://127.0.0.1:8000"

# Start Vue.js frontend
echo "🎨 Starting Vue.js frontend..."
cd alpha-strategy-frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 5

# Check if frontend is running
if ! curl -s http://localhost:5173 > /dev/null; then
    echo "❌ Frontend failed to start"
    cleanup
    exit 1
fi
echo "✅ Frontend running on http://localhost:5173"

echo ""
echo "🎉 Alpha Strategy Parser is now running!"
echo "========================================"
echo "🌐 Backend API:  http://127.0.0.1:8000"
echo "🎨 Frontend:     http://localhost:5173"
echo "📚 API Docs:     http://127.0.0.1:8000/docs"
echo ""
echo "💡 Quick Start:"
echo "   1. Open http://localhost:5173 in your browser"
echo "   2. Enter a strategy like: rsi(close, 14) > 70"
echo "   3. Click 'Execute Strategy'"
echo ""
echo "🛑 Press Ctrl+C to stop all services"

# Keep script running and wait for interrupt
wait 