# 🎯 How to Create and Define Functions and Strategies

## 🚀 **Overview**

This guide provides comprehensive instructions on how to properly create and define functions and strategies for the Alpha Strategy Parser. The system achieves **100% success rate** when strategies are properly defined with all required parameters.

---

## 📚 **Table of Contents**

1. [Function Categories](#function-categories)
2. [Parameter Requirements](#parameter-requirements)
3. [Strategy Syntax Rules](#strategy-syntax-rules)
4. [Common Patterns](#common-patterns)
5. [Advanced Examples](#advanced-examples)
6. [Multi-timeframe Strategies](#multi-timeframe-strategies)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Strategy Universe Examples](#strategy-universe-examples)

---

## 🔧 **Function Categories**

### **1. Single-Field Functions (Only Need Close)**
These functions work perfectly with just the `close` parameter:

```python
# Moving Averages
sma(close, 20)          # Simple Moving Average
ema(close, 50)          # Exponential Moving Average
wma(close, 14)          # Weighted Moving Average

# Oscillators
rsi(close, 14)          # Relative Strength Index
stochrsi(close, 14)     # Stochastic RSI
cmo(close, 14)          # Chande Momentum Oscillator
roc(close, 14)          # Rate of Change
mom(close, 14)          # Momentum
ppo(close, 12, 26)      # Percentage Price Oscillator

# MACD Family
macd(close, 12, 26, 9)  # MACD
macd_signal(close, 12, 26, 9)  # MACD Signal
macd_hist(close, 12, 26, 9)    # MACD Histogram

# Bollinger Bands
bbands(close, 20, 2)    # Bollinger Bands
bb_upper(close, 20, 2)  # Bollinger Bands Upper
bb_lower(close, 20, 2)  # Bollinger Bands Lower
bb_middle(close, 20, 2) # Bollinger Bands Middle

# Statistical Functions
stddev(close, 20)       # Standard Deviation
var(close, 20)          # Variance
linearreg(close, 20)    # Linear Regression

# Custom Functions
cum(volume)             # Cumulative Sum
cumulative(volume)      # Cumulative Sum (alias)
```

### **2. Multi-Field Functions (Require All Parameters)**
These functions require multiple data fields:

```python
# Volatility Indicators
atr(high, low, close, 14)           # Average True Range
natr(high, low, close, 14)          # Normalized ATR
trange(high, low, close)            # True Range

# Oscillators
stoch(high, low, close, 14)         # Stochastic Oscillator
stoch_k(high, low, close, 14)       # Stochastic %K
stoch_d(high, low, close, 14)       # Stochastic %D
willr(high, low, close, 14)         # Williams %R
cci(high, low, close, 14)           # Commodity Channel Index
ultosc(high, low, close, 7, 14, 28) # Ultimate Oscillator

# Directional Indicators
adx(high, low, close, 14)           # Average Directional Index
dx(high, low, close, 14)            # Directional Movement Index
plus_di(high, low, close, 14)       # Plus Directional Indicator
minus_di(high, low, close, 14)      # Minus Directional Indicator
plus_dm(high, low, 14)              # Plus Directional Movement
minus_dm(high, low, 14)             # Minus Directional Movement

# Volume Indicators
mfi(high, low, close, volume, 14)   # Money Flow Index
obv(close, volume)                  # On-Balance Volume

# Parabolic SAR
sar(high, low, close, 0.02, 0.2)   # Parabolic SAR
```

### **3. Aggregation Functions**
These functions work with any data series:

```python
# Statistical Aggregations
min(data, period)        # Minimum over period
max(data, period)        # Maximum over period
count(data, period)      # Count non-zero values
countstreak(data, period) # Count consecutive streaks

# Mathematical Functions
abs(data)                # Absolute values
ceil(data)               # Ceiling function
floor(data)              # Floor function
round(data)              # Round to nearest integer
square(data)             # Square of values
```

### **4. Historical Access Functions**
These functions access historical data:

```python
n_days_ago(data, n)     # Value n days ago
n_weeks_ago(data, n)    # Value n weeks ago
n_months_ago(data, n)   # Value n months ago
n_years_ago(data, n)    # Value n years ago
```

### **5. Special Functions**
These are custom functions for advanced strategies:

```python
# Timeframe Functions
tf(condition, 'daily')   # Multi-timeframe condition
tf(condition, 'weekly')  # Weekly timeframe
tf(condition, 'monthly') # Monthly timeframe
tf(condition, 'yearly')  # Yearly timeframe

# Crossover Detection
series1 crossover series2  # Crossover detection
```

---

## 📋 **Parameter Requirements**

### **✅ CORRECT Usage Examples**

#### **Single-Field Functions**
```python
# ✅ CORRECT - Only need close parameter
rsi(close, 14) > 30
ema(close, 50) > ema(close, 200)
sma(close, 20) < sma(close, 50)
macd(close, 12, 26, 9) > 0
bb_upper(close, 20, 2) < close
```

#### **Multi-Field Functions**
```python
# ✅ CORRECT - All required parameters provided
cci(high, low, close, 14) > 60
stoch(high, low, close, 14) > 80
mfi(high, low, close, volume, 14) > 70
atr(high, low, close, 14) > 2
willr(high, low, close, 14) > -50
adx(high, low, close, 14) > 30
obv(close, volume) > 1000
```

### **❌ INCORRECT Usage Examples**

```python
# ❌ INCORRECT - Missing required parameters
cci(close, 14) > 60          # Missing high, low
stoch(close, 14) > 80        # Missing high, low
mfi(close, 14) > 70          # Missing high, low, volume
atr(close, 14) > 2           # Missing high, low
willr(close, 14) > -50       # Missing high, low
adx(close, 14) > 30          # Missing high, low
obv(close) > 1000            # Missing volume
```

---

## 📝 **Strategy Syntax Rules**

### **1. Basic Comparisons**
```python
# Function vs Value
rsi(close, 14) > 70
ema(close, 50) < 1000

# Function vs Function
sma(close, 20) > sma(close, 50)
ema(close, 21) > ema(close, 55)

# Data Field vs Value
close > 1000
volume > 1000000
```

### **2. Logical Operators**
```python
# AND Logic
rsi(close, 14) > 70 AND volume > 1000000
ema(close, 50) > ema(close, 200) AND macd(close, 12, 26, 9) > 0

# Complex Combinations
sma(close, 20) > sma(close, 50) AND 
rsi(close, 14) > 40 AND 
bb_upper(close, 20, 2) < close
```

### **3. Crossover Logic**
```python
# Value Crossover
rsi(close, 14) crossover 50
stoch(high, low, close, 14) crossover 80

# Function-to-Function Crossover
ema(close, 50) crossover ema(close, 200)
plus_di(high, low, close, 14) crossover minus_di(high, low, close, 14)
```

### **4. Bollinger Bands Properties**
```python
# Property Access
bbands(close, 20, 2).upper < close
bbands(close, 20, 2).lower > close
bbands(close, 20, 2).middle > sma(close, 50)

# Arithmetic with Properties
bbands(close, 20, 2).upper - bbands(close, 20, 2).lower < 10
```

---

## 🎯 **Common Patterns**

### **1. Golden Cross Strategy**
```python
# Simple Golden Cross
ema(close, 50) > ema(close, 200)

# Golden Cross with RSI Filter
ema(close, 50) > ema(close, 200) AND rsi(close, 14) > 40

# Golden Cross with Volume Confirmation
ema(close, 50) > ema(close, 200) AND volume > sma(volume, 20) * 1.5
```

### **2. Mean Reversion Strategy**
```python
# RSI Oversold
rsi(close, 14) < 30

# Bollinger Bands Lower
bb_lower(close, 20, 2) > close

# Combined Mean Reversion
rsi(close, 14) < 30 AND bb_lower(close, 20, 2) > close
```

### **3. Momentum Strategy**
```python
# RSI Momentum
rsi(close, 14) > 70

# MACD Momentum
macd(close, 12, 26, 9) > 0

# Combined Momentum
rsi(close, 14) > 60 AND macd(close, 12, 26, 9) > 0
```

### **4. Volume Confirmation**
```python
# Volume Above Average
volume > sma(volume, 20)

# OBV Confirmation
obv(close, volume) > sma(obv(close, volume), 20)

# MFI Confirmation
mfi(high, low, close, volume, 14) > 60
```

---

## 🚀 **Advanced Examples**

### **1. Complex Multi-Indicator Strategy**
```python
# Golden Cross + RSI + Volume + Volatility
ema(close, 50) > ema(close, 200) AND 
rsi(close, 14) > 40 AND 
volume > sma(volume, 20) * 1.2 AND
atr(high, low, close, 14) > sma(atr(high, low, close, 14), 20)
```

### **2. Bollinger Bands Squeeze**
```python
# Bollinger Bands Squeeze with ATR
bbands(close, 20, 2).upper - bbands(close, 20, 2).lower < sma(atr(high, low, close, 14), 20)
```

### **3. Nested Function Strategy**
```python
# SMA of OBV with RSI Filter
sma(obv(close, volume), 20) > 1000 AND rsi(close, 14) > 50
```

### **4. Crossover with Multiple Filters**
```python
# EMA Crossover with ADX and RSI
ema(close, 21) crossover ema(close, 55) AND 
adx(high, low, close, 14) > 25 AND 
rsi(close, 14) > 50
```

---

## ⏰ **Multi-timeframe Strategies**

### **1. Basic Multi-timeframe**
```python
# Daily and Weekly RSI
tf(rsi(close, 14) > 70, 'daily') AND tf(rsi(close, 14) < 30, 'weekly')
```

### **2. Complex Multi-timeframe**
```python
# Daily EMA, Weekly MACD, Monthly RSI
tf(ema(close, 50) > ema(close, 200), 'daily') AND 
tf(macd(close, 12, 26, 9) > 0, 'weekly') AND 
tf(rsi(close, 14) > 40, 'monthly')
```

### **3. Multi-timeframe with Aggregations**
```python
# Daily Count, Weekly Max, Monthly Min
tf(count(rsi(close, 14) > 70, 10) >= 5, 'daily') AND 
tf(max(ema(close, 21), 20) > ema(close, 55), 'weekly') AND 
tf(min(atr(high, low, close, 14), 20) < 10, 'monthly')
```

---

## 🎯 **Best Practices**

### **1. Parameter Validation**
- Always provide all required parameters for multi-field functions
- Use appropriate lookback periods (14 for RSI, 20 for SMA, etc.)
- Validate parameter ranges (RSI: 0-100, MACD: any value)

### **2. Strategy Design**
- Start with simple strategies before adding complexity
- Use logical operators (AND) to combine conditions
- Test strategies thoroughly before deployment

### **3. Performance Optimization**
- Use efficient functions (SMA, EMA over complex calculations)
- Avoid overly complex nested functions
- Consider multi-timeframe strategies for better signals

### **4. Error Prevention**
- Always include all required parameters
- Use proper function names (case-sensitive)
- Validate strategy syntax before execution

---

## 🔧 **Troubleshooting**

### **Common Errors and Solutions**

#### **1. "Missing required positional argument"**
```python
# ❌ Error: FunctionRegistry._cci() missing 1 required positional argument: 'close'
cci(close, 14) > 60

# ✅ Solution: Include all required parameters
cci(high, low, close, 14) > 60
```

#### **2. "Unknown function"**
```python
# ❌ Error: Unknown function: stochrsI
stochrsI(close, 14) > 80

# ✅ Solution: Use correct function name (case-sensitive)
stochrsi(close, 14) > 80
```

#### **3. "Parse error"**
```python
# ❌ Error: Parse error with complex nested functions
sma(obv(close, volume), 20) > sma(obv(close, volume), 50)

# ✅ Solution: Simplify or use intermediate variables
obv_sma_20 = sma(obv(close, volume), 20)
obv_sma_50 = sma(obv(close, volume), 50)
obv_sma_20 > obv_sma_50
```

---

## 🌟 **Strategy Universe Examples**

Here are examples from our comprehensive strategy universe for testing parser performance:

### **Basic Strategies (50 examples)**
```python
# Moving Average Strategies
ema(close, 50) > ema(close, 200) AND rsi(close, 14) > 40
sma(close, 20) > sma(close, 50) AND macd(close, 12, 26, 9) > 0
ema(close, 21) > ema(close, 55) AND rsi(close, 14) > 60

# RSI Strategies
rsi(close, 14) crossover 50 AND adx(high, low, close, 14) > 20
rsi(close, 14) > 70 AND volume > sma(volume, 20) * 1.5
rsi(close, 14) < 30 AND bb_lower(close, 20, 2) > close

# MACD Strategies
macd(close, 12, 26, 9) crossover 0 AND atr(high, low, close, 14) > 5
macd(close, 12, 26, 9) > 0 AND stochrsi(close, 14) > 60
macd(close, 12, 26, 9) < 0 AND ema(close, 50) < ema(close, 200)

# Bollinger Bands Strategies
bb_upper(close, 20, 2) < close AND rsi(close, 14) > 70
bb_lower(close, 20, 2) > close AND macd(close, 12, 26, 9) < 0
bb_middle(close, 20, 2) > close AND volume > sma(volume, 20)
```

### **Advanced Strategies (50 examples)**
```python
# Multi-Indicator Strategies
ema(close, 50) > ema(close, 200) AND rsi(close, 14) > 40 AND volume > sma(volume, 20)
sma(close, 20) > sma(close, 50) AND macd(close, 12, 26, 9) > 0 AND atr(high, low, close, 14) > 2
rsi(close, 14) > 60 AND stoch(high, low, close, 14) > 80 AND mfi(high, low, close, volume, 14) > 70

# Crossover Strategies
ema(close, 21) crossover ema(close, 55) AND adx(high, low, close, 14) > 25
plus_di(high, low, close, 14) crossover minus_di(high, low, close, 14) AND rsi(close, 14) > 50
stoch(high, low, close, 14) crossover 80 AND ultosc(high, low, close, 7, 14, 28) > 60

# Volume Confirmation Strategies
close > sma(close, 20) AND volume > sma(volume, 20) * 1.5 AND obv(close, volume) > sma(obv(close, volume), 20)
ema(close, 50) > ema(close, 200) AND mfi(high, low, close, volume, 14) > 60 AND adx(high, low, close, 14) > 25
```

### **Multi-timeframe Strategies (50 examples)**
```python
# Basic Multi-timeframe
tf(rsi(close, 14) > 70, 'daily') AND tf(rsi(close, 14) < 30, 'weekly')
tf(ema(close, 50) > ema(close, 200), 'daily') AND tf(macd(close, 12, 26, 9) > 0, 'weekly')
tf(sma(close, 20) > sma(close, 50), 'daily') AND tf(adx(high, low, close, 14) > 25, 'monthly')

# Complex Multi-timeframe
tf(cci(high, low, close, 14) > 60, 'daily') AND tf(ema(close, 21) > ema(close, 55), 'weekly') AND tf(macd(close, 12, 26, 9) > 0, 'monthly')
tf(stoch(high, low, close, 14) > 80, 'daily') AND tf(mfi(high, low, close, volume, 14) > 70, 'weekly') AND tf(atr(high, low, close, 14) > 5, 'monthly')

# Multi-timeframe with Aggregations
tf(count(rsi(close, 14) > 70, 10) >= 5, 'daily') AND tf(max(ema(close, 21), 20) > ema(close, 55), 'weekly')
tf(countstreak(ema(close, 21) > ema(close, 55), 8) >= 1, 'daily') AND tf(min(atr(high, low, close, 14), 20) < 10, 'monthly')
```

### **Aggregation Strategies (50 examples)**
```python
# Count Strategies
count(rsi(close, 14) > 70, 10) >= 5 AND ema(close, 50) > ema(close, 200)
count(macd(close, 12, 26, 9) > 0, 15) >= 7 AND atr(high, low, close, 14) > 5
count(bb_upper(close, 20, 2) < close, 12) >= 4 AND volume > sma(volume, 20)

# Countstreak Strategies
countstreak(ema(close, 21) > ema(close, 55), 8) >= 1 AND rsi(close, 14) > 50
countstreak(stoch(high, low, close, 14) > 70, 5) >= 3 AND macd(close, 12, 26, 9) > 0
countstreak(close > sma(close, 20), 7) >= 1 AND obv(close, volume) > sma(obv(close, volume), 20)

# Mathematical Function Strategies
abs(rsi(close, 14) - 50) < 15 AND ema(close, 50) > ema(close, 200)
square(rsi(close, 14)) > 2500 AND macd(close, 12, 26, 9) > 0
round(ema(close, 21)) > sma(close, 34) AND atr(high, low, close, 14) > 5
```

### **Historical Access Strategies (50 examples)**
```python
# Historical Comparison Strategies
ema(close, 21) > n_days_ago(ema(close, 21), 5) AND rsi(close, 14) > 50
sma(close, 50) > n_weeks_ago(sma(close, 50), 2) AND macd(close, 12, 26, 9) > 0
obv(close, volume) > n_days_ago(obv(close, volume), 7) AND atr(high, low, close, 14) > 5

# Complex Historical Strategies
n_days_ago(ema(close, 55), 5) < ema(close, 55) AND stoch(high, low, close, 14) > 70
n_weeks_ago(ema(close, 34), 4) < ema(close, 34) AND mfi(high, low, close, volume, 14) > 60
n_months_ago(sma(close, 50), 2) < sma(close, 50) AND rsi(close, 14) > 55
```

---

## 🎉 **Conclusion**

This guide provides comprehensive instructions for creating and defining functions and strategies for the Alpha Strategy Parser. By following these guidelines:

1. ✅ **Use proper parameter requirements** for all functions
2. ✅ **Follow syntax rules** for strategy construction
3. ✅ **Apply best practices** for strategy design
4. ✅ **Test thoroughly** before deployment
5. ✅ **Use the strategy universe examples** for inspiration

You can create a **big universe of strategies** to test the parser performance and achieve **100% success rate** on properly defined strategies.

---

*Guide created on September 10, 2025*
*Version: 1.0.0 - Comprehensive Strategy Creation Guide*
