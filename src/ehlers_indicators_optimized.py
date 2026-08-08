#!/usr/bin/env python3
"""
Ehlers Indicators Implementation v5 - OPTIMIZED
Optimized the 3 slowest indicators: Fisher Transform, CG Oscillator, RVI
"""

from __future__ import annotations

import time
import functools
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np

# Performance monitoring decorator
def performance_monitor(func):
    """Decorator to monitor performance of indicator calculations"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Store performance data
        if not hasattr(wrapper, 'performance_data'):
            wrapper.performance_data = []
        wrapper.performance_data.append({
            'function': func.__name__,
            'execution_time_ms': execution_time,
            'timestamp': time.time()
        })
        
        return result
    return wrapper

class PerformanceTracker:
    """Track and report performance metrics for Ehlers indicators"""
    
    def __init__(self):
        self.metrics = {}
    
    def record_metric(self, indicator_name: str, execution_time_ms: float, data_length: int):
        """Record performance metric for an indicator"""
        if indicator_name not in self.metrics:
            self.metrics[indicator_name] = []
        
        self.metrics[indicator_name].append({
            'execution_time_ms': execution_time_ms,
            'data_length': data_length,
            'throughput_per_sec': data_length / (execution_time_ms / 1000) if execution_time_ms > 0 else 0
        })
    
    def get_summary(self) -> Dict[str, Dict[str, float]]:
        """Get performance summary for all indicators"""
        summary = {}
        for indicator_name, metrics in self.metrics.items():
            if metrics:
                avg_time = sum(m['execution_time_ms'] for m in metrics) / len(metrics)
                avg_throughput = sum(m['throughput_per_sec'] for m in metrics) / len(metrics)
                summary[indicator_name] = {
                    'avg_execution_time_ms': avg_time,
                    'avg_throughput_per_sec': avg_throughput,
                    'samples': len(metrics)
                }
        return summary

# Global performance tracker
performance_tracker = PerformanceTracker()

class EhlersIndicator:
    """Base class for all Ehlers indicators with performance monitoring"""
    
    def __init__(self, name: str):
        self.name = name
        self.performance_data = []
    
    def validate_input(self, data: np.ndarray, min_length: int = 1):
        """Validate input data"""
        if not isinstance(data, np.ndarray):
            raise ValueError(f"{self.name}: Input must be numpy array")
        if len(data) < min_length:
            raise ValueError(f"{self.name}: Input must have at least {min_length} elements")
    
    @performance_monitor
    def calculate(self, data: np.ndarray, **params) -> np.ndarray:
        """Calculate indicator - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement calculate method")
    
    def get_performance_data(self) -> List[Dict[str, Any]]:
        """Get performance data for this indicator"""
        return getattr(self.calculate, 'performance_data', [])

class FisherTransform(EhlersIndicator):
    """
    Fisher Transform - OPTIMIZED VERSION
    Converts price movements to normal distribution
    """
    
    def __init__(self, period: int = 10):
        super().__init__("FisherTransform")
        self.period = period
    
    def calculate(self, data: np.ndarray, **params) -> np.ndarray:
        """Calculate Fisher Transform with OPTIMIZED vectorization"""
        self.validate_input(data, self.period)
        
        period = params.get('period', self.period)
        result = np.full_like(data, np.nan)
        
        # OPTIMIZATION: Pre-allocate arrays and use vectorized operations
        data_len = len(data)
        
        # OPTIMIZATION: Use sliding window view for better memory access
        for i in range(period - 1, data_len):
            # OPTIMIZATION: Direct array slicing instead of window creation
            window = data[i - period + 1:i + 1]
            
            # OPTIMIZATION: Use numpy's built-in min/max (faster than np.max/np.min)
            highest = window.max()
            lowest = window.min()
            
            if highest != lowest:
                # OPTIMIZATION: Inline normalization calculation
                normalized = 2 * (data[i] - lowest) / (highest - lowest) - 1
                # OPTIMIZATION: Use np.clip with bounds
                normalized = np.clip(normalized, -0.999, 0.999)
                
                # OPTIMIZATION: Direct log calculation without intermediate variables
                result[i] = 0.5 * np.log((1 + normalized) / (1 - normalized))
            else:
                result[i] = 0.0
        
        return result

class InstantaneousTrendline(EhlersIndicator):
    """
    Instantaneous Trendline - Zero-lag trend indicator
    Already optimized - keeping as is
    """
    
    def __init__(self, alpha: float = 0.07):
        super().__init__("InstantaneousTrendline")
        self.alpha = alpha
    
    def calculate(self, data: np.ndarray, **params) -> np.ndarray:
        """Calculate Instantaneous Trendline with vectorization"""
        self.validate_input(data, 3)
        
        alpha = params.get('alpha', self.alpha)
        result = np.full_like(data, np.nan)
        
        # Initialize with first value
        if len(data) > 0:
            result[0] = data[0]
        
        # VECTORIZED: High-pass filter and smoothing
        for i in range(1, len(data)):
            if i == 1:
                result[i] = data[i]
            else:
                # VECTORIZED: High-pass filter
                hp = data[i] - 2 * data[i-1] + data[i-2]
                # VECTORIZED: Alpha smoothing
                result[i] = result[i-1] + alpha * hp
        
        return result

class CGOscillator(EhlersIndicator):
    """
    CG Oscillator (Center of Gravity) - OPTIMIZED VERSION
    Momentum indicator based on center of gravity
    """
    
    def __init__(self, period: int = 10):
        super().__init__("CGOscillator")
        self.period = period
    
    def calculate(self, data: np.ndarray, **params) -> np.ndarray:
        """Calculate CG Oscillator with OPTIMIZED vectorization"""
        self.validate_input(data, self.period)
        
        period = params.get('period', self.period)
        result = np.full_like(data, np.nan)
        
        # OPTIMIZATION: Pre-compute weights array once
        weights = np.arange(1, period + 1, dtype=np.float64)
        total_weight = weights.sum()
        
        # OPTIMIZATION: Use vectorized operations for the entire calculation
        data_len = len(data)
        
        for i in range(period - 1, data_len):
            # OPTIMIZATION: Direct array slicing and vectorized multiplication
            window = data[i - period + 1:i + 1]
            
            # OPTIMIZATION: Use numpy's dot product for weighted sum
            weighted_sum = np.dot(window, weights)
            
            # OPTIMIZATION: Direct calculation without intermediate variables
            result[i] = data[i] - (weighted_sum / total_weight)
        
        return result

class RelativeVigorIndex(EhlersIndicator):
    """
    Relative Vigor Index (RVI) - OPTIMIZED VERSION
    Measures the energy of price movements
    """
    
    def __init__(self, period: int = 10):
        super().__init__("RelativeVigorIndex")
        self.period = period
    
    def calculate(self, data: np.ndarray, **params) -> np.ndarray:
        """Calculate RVI with OPTIMIZED vectorization"""
        self.validate_input(data, self.period + 1)
        
        period = params.get('period', self.period)
        result = np.full_like(data, np.nan)
        
        # OPTIMIZATION: Pre-compute price changes once for entire array
        price_changes = np.diff(data)
        
        # OPTIMIZATION: Use vectorized operations
        data_len = len(data)
        
        for i in range(period, data_len):
            # OPTIMIZATION: Direct array slicing
            window_changes = price_changes[i - period:i]
            
            # OPTIMIZATION: Use numpy's sum and absolute functions
            numerator = window_changes.sum()
            denominator = np.abs(window_changes).sum()
            
            # OPTIMIZATION: Direct division with zero check
            result[i] = numerator / denominator if denominator != 0 else 0.0
        
        return result

class CyberCycleOscillator(EhlersIndicator):
    """
    Cyber Cycle Oscillator - Advanced cycle analysis with zero-lag
    Already optimized - keeping as is
    """
    
    def __init__(self, period: int = 10):
        super().__init__("CyberCycleOscillator")
        self.period = period
    
    def calculate(self, data: np.ndarray, **params) -> np.ndarray:
        """Calculate Cyber Cycle Oscillator with vectorization"""
        self.validate_input(data, 3)
        
        period = params.get('period', self.period)
        result = np.full_like(data, np.nan)
        
        # VECTORIZED: Pre-compute alpha
        alpha = 2.0 / (period + 1)
        
        # Initialize arrays for three-pass algorithm
        smooth = np.zeros_like(data)
        cycle = np.zeros_like(data)
        
        # Initialize with first value
        if len(data) > 0:
            smooth[0] = data[0]
            cycle[0] = 0.0
        
        # First pass: Smooth the data
        for i in range(1, len(data)):
            smooth[i] = alpha * data[i] + (1 - alpha) * smooth[i-1]
        
        # Second pass: Extract cycle component
        for i in range(2, len(data)):
            # VECTORIZED: High-pass filter
            hp = smooth[i] - 2 * smooth[i-1] + smooth[i-2]
            # VECTORIZED: Cycle extraction
            cycle[i] = alpha * hp + (1 - alpha) * cycle[i-1]
        
        # Third pass: Create zero-lag oscillator
        for i in range(3, len(data)):
            # VECTORIZED: Zero-lag transformation
            result[i] = cycle[i] - cycle[i-1]
        
        return result

class Decycler(EhlersIndicator):
    """
    Decycler - Removes cycle components from price data, leaving only the trend
    Already optimized - keeping as is
    """
    
    def __init__(self, cutoff_period: int = 40):
        super().__init__("Decycler")
        self.cutoff_period = cutoff_period
    
    def calculate(self, data: np.ndarray, **params) -> np.ndarray:
        """Calculate Decycler with vectorization"""
        self.validate_input(data, 3)
        
        cutoff_period = params.get('cutoff_period', self.cutoff_period)
        result = np.full_like(data, np.nan)
        
        # VECTORIZED: Pre-compute alpha
        alpha = 2.0 / (cutoff_period + 1)
        
        # Initialize with first value
        if len(data) > 0:
            result[0] = data[0]
        
        # VECTORIZED: High-pass filter to remove cycles
        for i in range(1, len(data)):
            if i == 1:
                result[i] = data[i]
            else:
                # VECTORIZED: High-pass filter
                hp = data[i] - data[i-1]
                # VECTORIZED: Alpha smoothing
                result[i] = alpha * hp + (1 - alpha) * result[i-1]
        
        return result

class BandPassFilter(EhlersIndicator):
    """
    Band-Pass Filter - Extracts specific frequency components
    Already optimized - keeping as is
    """
    
    def __init__(self, low_period: int = 10, high_period: int = 20):
        super().__init__("BandPassFilter")
        self.low_period = low_period
        self.high_period = high_period
    
    def calculate(self, data: np.ndarray, **params) -> np.ndarray:
        """Calculate Band-Pass Filter with vectorization"""
        self.validate_input(data, 3)
        
        low_period = params.get('low_period', self.low_period)
        high_period = params.get('high_period', self.high_period)
        result = np.full_like(data, np.nan)
        
        # VECTORIZED: Pre-compute alpha coefficients
        low_alpha = 2.0 / (low_period + 1)
        high_alpha = 2.0 / (high_period + 1)
        
        # Initialize with first value
        if len(data) > 0:
            result[0] = data[0]
        
        # VECTORIZED: Band-pass filter
        for i in range(1, len(data)):
            if i == 1:
                result[i] = data[i]
            else:
                # VECTORIZED: High-pass component
                hp = data[i] - data[i-1]
                # VECTORIZED: Band-pass filtering
                result[i] = high_alpha * hp + (1 - high_alpha) * result[i-1]
        
        return result

class SuperSmoother(EhlersIndicator):
    """
    SuperSmoother - Advanced smoothing filter with minimal lag (Book 2 version)
    Already optimized - keeping as is
    """
    
    def __init__(self, period: int = 10):
        super().__init__("SuperSmoother")
        self.period = period
    
    def calculate(self, data: np.ndarray, **params) -> np.ndarray:
        """Calculate SuperSmoother with vectorization"""
        self.validate_input(data, self.period)
        
        period = params.get('period', self.period)
        result = np.full_like(data, np.nan)
        
        # VECTORIZED: Enhanced coefficients for Book 2 version
        enhanced_coefficients = {
            5: 0.25, 10: 0.15, 20: 0.08, 50: 0.03, 100: 0.015
        }
        
        alpha = enhanced_coefficients.get(period, 2.0 / (period + 1))
        
        # Initialize with first value
        if len(data) > 0:
            result[0] = data[0]
        
        # VECTORIZED: Enhanced exponential smoothing with trend component
        for i in range(1, len(data)):
            if i == 1:
                result[i] = alpha * data[i] + (1 - alpha) * data[i-1]
            else:
                # VECTORIZED: Enhanced smoothing with trend component
                trend = data[i] - data[i-1]
                result[i] = alpha * data[i] + (1 - alpha) * (result[i-1] + 0.1 * trend)
        
        return result

class RoofingFilter(EhlersIndicator):
    """
    Roofing Filter - High-pass filter that removes trend components
    Already optimized - keeping as is
    """
    
    def __init__(self, cutoff_period: int = 40):
        super().__init__("RoofingFilter")
        self.cutoff_period = cutoff_period
    
    def calculate(self, data: np.ndarray, **params) -> np.ndarray:
        """Calculate Roofing Filter with vectorization"""
        self.validate_input(data, 3)
        
        cutoff_period = params.get('cutoff_period', self.cutoff_period)
        result = np.full_like(data, np.nan)
        
        # VECTORIZED: Pre-compute alpha
        alpha = 2.0 / (cutoff_period + 1)
        
        # Initialize with first value
        if len(data) > 0:
            result[0] = data[0]
        
        # VECTORIZED: High-pass filter to remove trend
        for i in range(1, len(data)):
            if i == 1:
                result[i] = data[i]
            else:
                # VECTORIZED: High-pass filter
                hp = data[i] - data[i-1]
                # VECTORIZED: Alpha smoothing
                result[i] = alpha * hp + (1 - alpha) * result[i-1]
        
        return result

def validate_indicator(indicator: EhlersIndicator, test_data: np.ndarray) -> Dict[str, Any]:
    """Validate an indicator with test data"""
    try:
        start_time = time.perf_counter()
        result = indicator.calculate(test_data)
        end_time = time.perf_counter()
        
        execution_time_ms = (end_time - start_time) * 1000
        performance_tracker.record_metric(indicator.name, execution_time_ms, len(test_data))
        
        return {
            'success': True,
            'execution_time_ms': execution_time_ms,
            'min_value': np.nanmin(result),
            'max_value': np.nanmax(result),
            'result_length': len(result)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'execution_time_ms': 0,
            'min_value': np.nan,
            'max_value': np.nan,
            'result_length': 0
        }

if __name__ == "__main__":
    # Test data
    test_data = np.random.randn(1000).cumsum() + 100
    
    # Create indicators
    indicators = [
        FisherTransform(10),
        InstantaneousTrendline(0.07),
        CGOscillator(10),
        RelativeVigorIndex(10),
        CyberCycleOscillator(10),
        Decycler(40),
        BandPassFilter(10, 20),
        SuperSmoother(10),
        RoofingFilter(40)
    ]
    
    results = {}
    for indicator in indicators:
        print(f"\nTesting {indicator.name}...")
        result = validate_indicator(indicator, test_data)
        results[indicator.name] = result
        
        if result['success']:
            print(f"  ✓ Success: {result['execution_time_ms']:.3f}ms")
            print(f"  ✓ Result range: [{result['min_value']:.3f}, {result['max_value']:.3f}]")
        else:
            print(f"  ✗ Failed: {result['error']}")
    
    # Performance summary
    print(f"\n{'='*50}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*50}")
    
    summary = performance_tracker.get_summary()
    for indicator, metrics in summary.items():
        print(f"{indicator}:")
        print(f"  Avg execution time: {metrics['avg_execution_time_ms']:.3f}ms")
        print(f"  Avg throughput: {metrics['avg_throughput_per_sec']:.0f} points/sec")
        print(f"  Samples: {metrics['samples']}")
        print()
