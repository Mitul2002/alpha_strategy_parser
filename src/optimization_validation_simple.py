#!/usr/bin/env python3
"""
Optimization Validation Test (Simple Version)
Compare optimized vs non-optimized versions of Fisher Transform, CG Oscillator, and RVI
Test on 50 symbols with MSE error analysis
"""

import numpy as np
import pandas as pd
from pathlib import Path
import time
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Import both versions
from ehlers_indicators import (
    FisherTransform as OptimizedFisher,
    CGOscillator as OptimizedCG,
    RelativeVigorIndex as OptimizedRVI
)

# Create non-optimized versions for comparison
class NonOptimizedFisher:
    def __init__(self, period: int = 10):
        self.period = period
        self.name = "FisherTransform"
    
    def calculate(self, data: np.ndarray, **params) -> np.ndarray:
        period = params.get('period', self.period)
        result = np.full_like(data, np.nan)
        
        # NON-OPTIMIZED: Original implementation
        for i in range(period - 1, len(data)):
            window = data[i - period + 1:i + 1]
            
            # NON-OPTIMIZED: Using np.max/np.min functions
            highest = np.max(window)
            lowest = np.min(window)
            
            if highest != lowest:
                # NON-OPTIMIZED: Multiple intermediate calculations
                normalized = 2 * (data[i] - lowest) / (highest - lowest) - 1
                normalized = np.clip(normalized, -0.999, 0.999)
                
                # NON-OPTIMIZED: Separate log calculation with intermediate variables
                numerator = 1 + normalized
                denominator = 1 - normalized
                ratio = numerator / denominator
                result[i] = 0.5 * np.log(ratio)
            else:
                result[i] = 0.0
        
        return result

class NonOptimizedCG:
    def __init__(self, period: int = 10):
        self.period = period
        self.name = "CGOscillator"
    
    def calculate(self, data: np.ndarray, **params) -> np.ndarray:
        period = params.get('period', self.period)
        result = np.full_like(data, np.nan)
        
        # NON-OPTIMIZED: Recalculating total weight every time
        total_weight = period * (period + 1) / 2
        
        for i in range(period - 1, len(data)):
            window = data[i - period + 1:i + 1]
            
            # NON-OPTIMIZED: Manual weighted sum calculation
            weighted_sum = 0
            for j in range(period):
                weighted_sum += window[j] * (j + 1)
            
            # NON-OPTIMIZED: Separate center of gravity calculation
            cg = weighted_sum / total_weight
            result[i] = data[i] - cg
        
        return result

class NonOptimizedRVI:
    def __init__(self, period: int = 10):
        self.period = period
        self.name = "RelativeVigorIndex"
    
    def calculate(self, data: np.ndarray, **params) -> np.ndarray:
        period = params.get('period', self.period)
        result = np.full_like(data, np.nan)
        
        for i in range(period, len(data)):
            # NON-OPTIMIZED: Recalculating price changes for each window
            window_data = data[i - period:i + 1]
            price_changes = []
            for j in range(1, len(window_data)):
                price_changes.append(window_data[j] - window_data[j-1])
            
            # NON-OPTIMIZED: Manual sum calculations
            numerator = sum(price_changes)
            denominator = sum(abs(x) for x in price_changes)
            
            if denominator != 0:
                result[i] = numerator / denominator
            else:
                result[i] = 0.0
        
        return result

class OptimizationValidator:
    """Validate optimization accuracy and performance"""
    
    def __init__(self):
        self.optimized_indicators = {
            'fisher_transform': OptimizedFisher(10),
            'cg_oscillator': OptimizedCG(10),
            'relative_vigor_index': OptimizedRVI(10)
        }
        
        self.non_optimized_indicators = {
            'fisher_transform': NonOptimizedFisher(10),
            'cg_oscillator': NonOptimizedCG(10),
            'relative_vigor_index': NonOptimizedRVI(10)
        }
        
        self.results = {}
    
    def generate_synthetic_data(self, num_symbols: int = 50, data_length: int = 1000) -> Dict[str, np.ndarray]:
        """Generate synthetic price data for testing"""
        synthetic_data = {}
        
        for i in range(num_symbols):
            symbol = f"SYMBOL_{i:03d}"
            
            # Generate realistic price data with trend, cycles, and noise
            np.random.seed(i)  # For reproducible results
            
            # Base trend
            trend = np.linspace(100, 150, data_length)
            
            # Add cyclical component
            cycle = 10 * np.sin(np.linspace(0, 4*np.pi, data_length))
            
            # Add noise
            noise = 0.5 * np.random.randn(data_length)
            
            # Combine components
            price_data = trend + cycle + noise
            
            synthetic_data[symbol] = price_data
        
        return synthetic_data
    
    def calculate_mse(self, optimized_result: np.ndarray, non_optimized_result: np.ndarray) -> float:
        """Calculate Mean Squared Error between two results"""
        # Remove NaN values for comparison
        mask = ~(np.isnan(optimized_result) | np.isnan(non_optimized_result))
        
        if np.sum(mask) == 0:
            return 0.0
        
        optimized_clean = optimized_result[mask]
        non_optimized_clean = non_optimized_result[mask]
        
        mse = np.mean((optimized_clean - non_optimized_clean) ** 2)
        return mse
    
    def calculate_error_percentage(self, optimized_result: np.ndarray, non_optimized_result: np.ndarray) -> float:
        """Calculate error percentage"""
        # Remove NaN values for comparison
        mask = ~(np.isnan(optimized_result) | np.isnan(non_optimized_result))
        
        if np.sum(mask) == 0:
            return 0.0
        
        optimized_clean = optimized_result[mask]
        non_optimized_clean = non_optimized_result[mask]
        
        # Calculate relative error percentage
        error = np.abs(optimized_clean - non_optimized_clean)
        reference = np.abs(non_optimized_clean)
        
        # Avoid division by zero
        reference = np.where(reference == 0, 1e-10, reference)
        
        error_percentage = np.mean(error / reference) * 100
        return error_percentage
    
    def test_indicator_accuracy(self, indicator_name: str, synthetic_data: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Test accuracy of optimized vs non-optimized indicator"""
        print(f"\nTesting {indicator_name} accuracy...")
        
        optimized_indicator = self.optimized_indicators[indicator_name]
        non_optimized_indicator = self.non_optimized_indicators[indicator_name]
        
        mse_values = []
        error_percentages = []
        execution_times_optimized = []
        execution_times_non_optimized = []
        data_lengths = []
        
        for symbol, data in synthetic_data.items():
            # Test optimized version
            start_time = time.perf_counter()
            optimized_result = optimized_indicator.calculate(data)
            optimized_time = (time.perf_counter() - start_time) * 1000
            
            # Test non-optimized version
            start_time = time.perf_counter()
            non_optimized_result = non_optimized_indicator.calculate(data)
            non_optimized_time = (time.perf_counter() - start_time) * 1000
            
            # Calculate accuracy metrics
            mse = self.calculate_mse(optimized_result, non_optimized_result)
            error_percentage = self.calculate_error_percentage(optimized_result, non_optimized_result)
            
            mse_values.append(mse)
            error_percentages.append(error_percentage)
            execution_times_optimized.append(optimized_time)
            execution_times_non_optimized.append(non_optimized_time)
            data_lengths.append(len(data))
        
        return {
            'indicator_name': indicator_name,
            'symbols_tested': len(mse_values),
            'mse_values': mse_values,
            'error_percentages': error_percentages,
            'execution_times_optimized': execution_times_optimized,
            'execution_times_non_optimized': execution_times_non_optimized,
            'data_lengths': data_lengths,
            'avg_mse': np.mean(mse_values),
            'avg_error_percentage': np.mean(error_percentages),
            'max_error_percentage': np.max(error_percentages),
            'min_error_percentage': np.min(error_percentages),
            'std_error_percentage': np.std(error_percentages),
            'avg_optimized_time': np.mean(execution_times_optimized),
            'avg_non_optimized_time': np.mean(execution_times_non_optimized),
            'speedup_factor': np.mean(execution_times_non_optimized) / np.mean(execution_times_optimized)
        }
    
    def run_validation_test(self, num_symbols: int = 50) -> Dict[str, Any]:
        """Run complete validation test"""
        print("OPTIMIZATION VALIDATION TEST")
        print("=" * 50)
        
        # Generate synthetic data
        print(f"Generating synthetic data for {num_symbols} symbols...")
        synthetic_data = self.generate_synthetic_data(num_symbols)
        print(f"Generated data for {len(synthetic_data)} symbols")
        
        # Test each indicator
        results = {}
        for indicator_name in self.optimized_indicators.keys():
            result = self.test_indicator_accuracy(indicator_name, synthetic_data)
            results[indicator_name] = result
        
        self.results = results
        return results
    
    def create_text_visualization(self):
        """Create text-based visualization of results"""
        if not self.results:
            print("No results to visualize. Run validation test first.")
            return
        
        print("\n" + "="*80)
        print("OPTIMIZATION VALIDATION RESULTS VISUALIZATION")
        print("="*80)
        
        # Create bar charts using text
        indicators = list(self.results.keys())
        avg_errors = [self.results[ind]['avg_error_percentage'] for ind in indicators]
        max_errors = [self.results[ind]['max_error_percentage'] for ind in indicators]
        speedup_factors = [self.results[ind]['speedup_factor'] for ind in indicators]
        
        # Error percentage visualization
        print("\n📊 ERROR PERCENTAGE COMPARISON:")
        print("-" * 50)
        max_error = max(max(avg_errors), max(max_errors))
        
        for i, (indicator, avg_err, max_err) in enumerate(zip(indicators, avg_errors, max_errors)):
            print(f"\n{indicator.replace('_', ' ').upper()}:")
            
            # Average error bar
            avg_bar_length = int((avg_err / max_error) * 40)
            avg_bar = "█" * avg_bar_length + "░" * (40 - avg_bar_length)
            print(f"  Average Error: {avg_bar} {avg_err:.6f}%")
            
            # Max error bar
            max_bar_length = int((max_err / max_error) * 40)
            max_bar = "█" * max_bar_length + "░" * (40 - max_bar_length)
            print(f"  Maximum Error: {max_bar} {max_err:.6f}%")
        
        # Speedup visualization
        print(f"\n🚀 SPEEDUP FACTOR COMPARISON:")
        print("-" * 50)
        max_speedup = max(speedup_factors)
        
        for indicator, speedup in zip(indicators, speedup_factors):
            bar_length = int((speedup / max_speedup) * 40)
            bar = "█" * bar_length + "░" * (40 - bar_length)
            print(f"{indicator.replace('_', ' ').upper():<25}: {bar} {speedup:.1f}x")
        
        # Performance comparison table
        print(f"\n📈 PERFORMANCE COMPARISON TABLE:")
        print("-" * 80)
        print(f"{'Indicator':<20} {'Avg Error %':<12} {'Max Error %':<12} {'Speedup':<10} {'Status':<15}")
        print("-" * 80)
        
        for indicator, result in self.results.items():
            avg_err = result['avg_error_percentage']
            max_err = result['max_error_percentage']
            speedup = result['speedup_factor']
            
            # Determine status
            if max_err < 0.001 and speedup > 2.0:
                status = "✅ EXCELLENT"
            elif max_err < 0.01 and speedup > 1.5:
                status = "✅ GOOD"
            elif max_err < 0.1 and speedup > 1.2:
                status = "⚠️  ACCEPTABLE"
            else:
                status = "❌ NEEDS REVIEW"
            
            print(f"{indicator.replace('_', ' '):<20} {avg_err:<12.6f} {max_err:<12.6f} {speedup:<10.1f} {status:<15}")
    
    def print_summary_report(self):
        """Print comprehensive summary report"""
        if not self.results:
            print("No results to report. Run validation test first.")
            return
        
        print("\n" + "="*60)
        print("OPTIMIZATION VALIDATION SUMMARY REPORT")
        print("="*60)
        
        for indicator_name, result in self.results.items():
            print(f"\n{indicator_name.upper().replace('_', ' ')}:")
            print(f"  Symbols Tested: {result['symbols_tested']}")
            print(f"  Average Error: {result['avg_error_percentage']:.8f}%")
            print(f"  Maximum Error: {result['max_error_percentage']:.8f}%")
            print(f"  Minimum Error: {result['min_error_percentage']:.8f}%")
            print(f"  Error Std Dev: {result['std_error_percentage']:.8f}%")
            print(f"  Average MSE: {result['avg_mse']:.10f}")
            print(f"  Average Optimized Time: {result['avg_optimized_time']:.3f}ms")
            print(f"  Average Non-Optimized Time: {result['avg_non_optimized_time']:.3f}ms")
            print(f"  Speedup Factor: {result['speedup_factor']:.1f}x")
        
        # Overall summary
        all_avg_errors = [result['avg_error_percentage'] for result in self.results.values()]
        all_max_errors = [result['max_error_percentage'] for result in self.results.values()]
        all_speedups = [result['speedup_factor'] for result in self.results.values()]
        
        print(f"\nOVERALL SUMMARY:")
        print(f"  Average Error Across All Indicators: {np.mean(all_avg_errors):.8f}%")
        print(f"  Maximum Error Across All Indicators: {np.max(all_max_errors):.8f}%")
        print(f"  Average Speedup Across All Indicators: {np.mean(all_speedups):.1f}x")
        print(f"  Minimum Speedup: {np.min(all_speedups):.1f}x")
        print(f"  Maximum Speedup: {np.max(all_speedups):.1f}x")
        
        # Validation conclusion
        max_error = np.max(all_max_errors)
        avg_speedup = np.mean(all_speedups)
        
        print(f"\nVALIDATION CONCLUSION:")
        if max_error < 0.001:  # Less than 0.001% error
            print(f"  ✅ EXCELLENT: Maximum error is {max_error:.8f}% (very low)")
        elif max_error < 0.01:  # Less than 0.01% error
            print(f"  ✅ GOOD: Maximum error is {max_error:.8f}% (low)")
        elif max_error < 0.1:  # Less than 0.1% error
            print(f"  ⚠️  ACCEPTABLE: Maximum error is {max_error:.8f}% (moderate)")
        else:
            print(f"  ❌ HIGH ERROR: Maximum error is {max_error:.8f}% (needs review)")
        
        if avg_speedup > 2.0:
            print(f"  ✅ EXCELLENT: Average speedup is {avg_speedup:.1f}x (significant improvement)")
        elif avg_speedup > 1.5:
            print(f"  ✅ GOOD: Average speedup is {avg_speedup:.1f}x (good improvement)")
        elif avg_speedup > 1.2:
            print(f"  ⚠️  MODERATE: Average speedup is {avg_speedup:.1f}x (some improvement)")
        else:
            print(f"  ❌ LOW: Average speedup is {avg_speedup:.1f}x (minimal improvement)")

def main():
    """Main function to run optimization validation"""
    print("Starting Optimization Validation Test...")
    
    # Initialize validator
    validator = OptimizationValidator()
    
    # Run validation test
    results = validator.run_validation_test(num_symbols=50)
    
    # Print summary report
    validator.print_summary_report()
    
    # Create text visualization
    validator.create_text_visualization()
    
    print("\nOptimization validation test completed!")

if __name__ == "__main__":
    main()
