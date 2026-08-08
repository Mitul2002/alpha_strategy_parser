# 📁 Examples Directory

This directory contains example strategies and configuration files for the Alpha Strategy Parser.

## 📋 **Contents**

### **Strategy Files**
- `strats_all.txt` - Complete collection of all strategies
- `strat_focus_count.txt` - Count-focused strategies
- `strat_focus_obv.txt` - OBV-focused strategies
- `STRATEGY_UNIVERSE_EXAMPLES.txt` - Comprehensive strategy universe for testing

### **Configuration Files**
- `mock_backend_response.json` - Mock backend response for testing
- `mock_server.py` - Mock server for testing

## 🎯 **Strategy Universe Examples**

The `STRATEGY_UNIVERSE_EXAMPLES.txt` file contains **500+ example strategies** organized into categories:

### **Categories**
1. **Basic Strategies** (100 examples) - Simple indicator combinations
2. **Multi-timeframe Strategies** (100 examples) - Timeframe-based strategies
3. **Aggregation Strategies** (100 examples) - Count, countstreak, mathematical functions
4. **Historical Access Strategies** (100 examples) - Historical data comparisons
5. **Complex Nested Strategies** (100 examples) - Advanced nested function combinations
6. **Crossover Strategies** (100 examples) - Crossover detection strategies

### **Usage**
These examples can be used to:
- Test parser performance across a wide variety of strategies
- Validate 100% success rate on properly defined strategies
- Benchmark system performance
- Create new strategy variations

## 🚀 **Quick Start**

```bash
# Test a single strategy
python scripts/live_strategy_tester.py

# Test all strategies
python scripts/test_all_strategies.py

# Run comprehensive profiling
python ../profiling_scripts/CRITICAL_PROFILING_TEST.py
```

## 📚 **Documentation**

For detailed information on creating strategies, see:
- `../docs/howto.md` - Comprehensive strategy creation guide
- `../docs/USER_GUIDE.md` - Complete user guide
- `../analysis_reports/` - Analysis and performance reports
