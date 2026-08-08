#!/bin/bash

echo "🚀 Starting Alpha Strategy Parser System..."

# Kill any existing processes
pkill -f "python.*app.py" 2>/dev/null
pkill -f "vite" 2>/dev/null

# Start FastAPI backend from the main directory
echo "🔧 Starting FastAPI backend..."
cd webapi && source ../venv/bin/activate && PYTHONPATH=.. python app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start Vue.js frontend
echo "�� Starting Vue.js frontend..."
cd ../alpha-strategy-frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Services started successfully!"
echo "�� Backend API: http://127.0.0.1:8000"
echo "🎯 Frontend UI: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait
