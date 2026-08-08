@echo off
echo 🚀 Starting Alpha Strategy Parser...
echo ==================================

REM Check if we're in the right directory
if not exist "webapi\app.py" (
    echo ❌ Error: Please run this script from the alpha_strategy_parser directory
    echo    Current directory: %CD%
    echo    Expected: alpha_strategy_parser\
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Error: Virtual environment not found. Please run setup first:
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if frontend dependencies are installed
if not exist "alpha-strategy-frontend\node_modules" (
    echo ❌ Error: Frontend dependencies not installed. Please run:
    echo    cd alpha-strategy-frontend
    echo    npm install
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating Python virtual environment...
call venv\Scripts\activate.bat

REM Start FastAPI backend
echo 🌐 Starting FastAPI backend...
start "Backend" cmd /k "cd webapi && python app.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start Vue.js frontend
echo 🎨 Starting Vue.js frontend...
start "Frontend" cmd /k "cd alpha-strategy-frontend && npm run dev"

echo.
echo 🎉 Alpha Strategy Parser is now running!
echo ========================================
echo 🌐 Backend API:  http://127.0.0.1:8000
echo 🎨 Frontend:     http://localhost:5173
echo 📚 API Docs:     http://127.0.0.1:8000/docs
echo.
echo 💡 Quick Start:
echo    1. Open http://localhost:5173 in your browser
echo    2. Enter a strategy like: rsi(close, 14) > 70
echo    3. Click 'Execute Strategy'
echo.
echo 🛑 Close the command windows to stop services
pause 