#!/bin/bash

# Alpha Strategy Parser - Frontend Launcher
# Opens the web interface in your default browser

echo "🚀 Alpha Strategy Parser - Frontend Launcher"
echo "=============================================="

# Check if the API is running
if ! curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo "❌ Error: API is not running on http://127.0.0.1:8000"
    echo "Please start the API first:"
    echo "  cd webapi && python app.py"
    exit 1
fi

echo "✅ API is running on http://127.0.0.1:8000"
echo "🌐 Opening frontend in your default browser..."

# Open the frontend in the default browser
if command -v xdg-open > /dev/null; then
    # Linux
    xdg-open http://127.0.0.1:8000/
elif command -v open > /dev/null; then
    # macOS
    open http://127.0.0.1:8000/
elif command -v start > /dev/null; then
    # Windows
    start http://127.0.0.1:8000/
else
    echo "❌ Could not automatically open browser"
    echo "Please manually open: http://127.0.0.1:8000/"
fi

echo ""
echo "🎯 Frontend Features:"
echo "  • Enter strategies in natural language"
echo "  • View detailed trade analysis"
echo "  • See performance metrics"
echo "  • Analyze different timeframes"
echo ""
echo "💡 Example strategies:"
echo "  • close > 1000"
echo "  • rsi(close, 14) < 30"
echo "  • sma(close, 20) > sma(close, 50)"
echo "  • close > 1000 AND volume > 1000000" 