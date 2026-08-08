#!/bin/bash

# Alpha Strategy Parser - Deployment Script
# Sets up the testing environment for human users

echo "🚀 Alpha Strategy Parser - Deployment Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if we're in the right directory
if [ ! -f "src/function_registry.py" ]; then
    print_error "Please run this script from the alpha_strategy_parser directory"
    exit 1
fi

print_header "🔧 Setting up Alpha Strategy Parser Testing Environment"

# Step 1: Check Python version
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1)
if [ $? -eq 0 ]; then
    print_status "Python version: $python_version"
else
    print_error "Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Step 2: Check if virtual environment exists
if [ -d "venv" ]; then
    print_status "Virtual environment already exists"
    print_warning "To recreate, delete 'venv' directory and run again"
else
    print_status "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
fi

# Step 3: Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Step 4: Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Step 5: Install required packages
print_status "Installing required packages..."
pip install numpy pandas ta-lib pytest

# Check if ta-lib installation was successful
if ! python3 -c "import talib" 2>/dev/null; then
    print_warning "TA-Lib installation failed. This is common on some systems."
    print_warning "You can still use the parser without technical indicators."
    print_warning "To install TA-Lib manually:"
    echo "  Ubuntu/Debian: sudo apt-get install ta-lib"
    echo "  macOS: brew install ta-lib"
    echo "  Windows: Download from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib"
fi

# Step 6: Generate multi-timeframe data if it doesn't exist
if [ ! -d "../data_multi_timeframe" ]; then
    print_status "Generating multi-timeframe data..."
    python3 generate_timeframes.py
    if [ $? -ne 0 ]; then
        print_warning "Failed to generate multi-timeframe data"
        print_warning "You can still use daily data only"
    fi
else
    print_status "Multi-timeframe data already exists"
fi

# Step 7: Run basic tests
print_status "Running basic system tests..."
python3 test_integrated_system.py

# Step 8: Create quick start script
print_status "Creating quick start script..."
cat > quick_start.py << 'EOF'
#!/usr/bin/env python3
"""
Quick Start Script for Alpha Strategy Parser
Run this to test basic functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from simple_parser import SimpleStrategyParser
from strategy_executor import StrategyExecutor
from multi_timeframe_loader import MultiTimeframeLoader

def quick_test():
    print("🚀 Alpha Strategy Parser - Quick Start Test")
    print("=" * 50)
    
    # Test parser
    parser = SimpleStrategyParser()
    strategy = "rsi(close, 14) > 30 AND volume > sma(volume, 20)"
    
    print(f"📝 Testing strategy: {strategy}")
    parsed = parser.parse(strategy)
    
    if parsed:
        print("✅ Strategy parsed successfully!")
        print(f"📊 Structure: {parsed['type']}")
        
        # Test execution
        try:
            loader = MultiTimeframeLoader()
            data = loader.load_stock_data('RELIANCE', 'daily')
            
            if data:
                executor = StrategyExecutor()
                signals = executor.execute(parsed, data)
                
                buy_signals = sum(signals)
                total_signals = len(signals)
                success_rate = buy_signals / total_signals * 100
                
                print(f"⚡ Strategy executed successfully!")
                print(f"📊 Results: {buy_signals:,}/{total_signals:,} buy signals ({success_rate:.1f}%)")
                print("🎉 System is working perfectly!")
            else:
                print("⚠️  Could not load data, but parser is working")
                
        except Exception as e:
            print(f"⚠️  Execution failed: {e}")
            print("💡 This might be due to missing TA-Lib installation")
    else:
        print("❌ Strategy parsing failed")
        print("💡 Check your installation")

if __name__ == "__main__":
    quick_test()
EOF

chmod +x quick_start.py

# Step 9: Create requirements.txt
print_status "Creating requirements.txt..."
cat > requirements.txt << 'EOF'
numpy>=1.20.0
pandas>=1.3.0
ta-lib>=0.4.0
pytest>=6.0.0
EOF

# Step 10: Create README
print_status "Creating README.md..."
cat > README.md << 'EOF'
# Alpha Strategy Parser

A powerful, high-performance trading strategy parser with multi-timeframe support and advanced technical indicators.

## 🚀 Quick Start

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Run quick test:**
   ```bash
   python quick_start.py
   ```

3. **Run comprehensive demo:**
   ```bash
   python demo_final_comprehensive.py
   ```

## 📊 Features

- **30+ Technical Indicators** (RSI, SMA, EMA, MACD, Bollinger Bands, etc.)
- **4 Timeframes** (Daily, Weekly, Monthly, Yearly)
- **6 Stocks** with 23+ years of real market data
- **Advanced AND/OR Logic** support
- **Aggregation Functions** (min, max, count, countstreak, etc.)
- **Historical Data Access** (n_days_ago, n_weeks_ago, etc.)
- **High Performance** (60M+ records/second)

## 🔧 Installation

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install ta-lib

# Install Python dependencies
pip install -r requirements.txt
```

## 📖 Usage Examples

See `docs/USER_GUIDE.md` for detailed usage instructions and examples.

## 🧪 Testing

```bash
# Run all tests
python test_integrated_system.py

# Test specific functionality
python test_and_or_fix.py
```

## 📁 Project Structure

- `src/` - Core parser components
- `docs/` - Documentation and user guides
- `tests/` - Test files
- `demos/` - Example scripts and demonstrations
EOF

print_header "🎉 Deployment Complete!"
print_status "Your Alpha Strategy Parser testing environment is ready!"
print_status ""
print_status "Next steps:"
print_status "1. Activate virtual environment: source venv/bin/activate"
print_status "2. Run quick test: python quick_start.py"
print_status "3. Read documentation: docs/USER_GUIDE.md"
print_status "4. Run comprehensive demo: python demo_final_comprehensive.py"
print_status ""
print_status "Happy trading! 🚀📈"

# Deactivate virtual environment
deactivate 