#!/usr/bin/env python3
"""
Optimization Validation Test
Compare optimized vs non-optimized versions of Fisher Transform, CG Oscillator, and RVI
Test on 50 symbols with MSE error analysis and visualization
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
    
    def __init__(self, data_path: str = "../context/rsi_forward_returns/data_partitioned"):
        self.data_path = Path(data_path)
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
    
    def get_available_symbols(self, limit: int = 50) -> List[str]:
        """Get available symbols from data directory"""
        symbols = []
        if self.data_path.exists():
            for file_path in self.data_path.glob("symbol=*/"):
                symbol = file_path.name.replace("symbol=", "")
                symbols.append(symbol)
                if len(symbols) >= limit:
                    break
        return sorted(symbols)
    
    def load_symbol_data(self, symbol: str) -> np.ndarray:
        """Load price data for a symbol"""
        try:
            data_path = self.data_path / f"symbol={symbol}"
            parquet_file = data_path / f"symbol={symbol}.parquet"
            
            if not parquet_file.exists():
                return None
            
            # Load data using pandas
            df = pd.read_parquet(parquet_file)
            return df['close'].values
            
        except Exception as e:
            print(f"Error loading {symbol}: {e}")
            return None
    
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
    
    def test_indicator_accuracy(self, indicator_name: str, symbols: List[str]) -> Dict[str, Any]:
        """Test accuracy of optimized vs non-optimized indicator"""
        print(f"\nTesting {indicator_name} accuracy...")
        
        optimized_indicator = self.optimized_indicators[indicator_name]
        non_optimized_indicator = self.non_optimized_indicators[indicator_name]
        
        mse_values = []
        error_percentages = []
        execution_times_optimized = []
        execution_times_non_optimized = []
        data_lengths = []
        
        for symbol in symbols:
            data = self.load_symbol_data(symbol)
            if data is None or len(data) < 50:
                continue
            
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
            'avg_optimized_time': np.mean(execution_times_optimized),
            'avg_non_optimized_time': np.mean(execution_times_non_optimized),
            'speedup_factor': np.mean(execution_times_non_optimized) / np.mean(execution_times_optimized)
        }
    
    def run_validation_test(self, num_symbols: int = 50) -> Dict[str, Any]:
        """Run complete validation test"""
        print("OPTIMIZATION VALIDATION TEST")
        print("=" * 50)
        
        # Get symbols
        symbols = self.get_available_symbols(num_symbols)
        print(f"Testing with {len(symbols)} symbols")
        
        if len(symbols) == 0:
            print("No symbols found, generating synthetic data...")
            # Generate synthetic data for testing
            symbols = [f"SYMBOL_{i:03d}" for i in range(num_symbols)]
            synthetic_data = {}
            for symbol in symbols:
                # Generate realistic price data
                data = 100 + np.cumsum(np.random.randn(1000) * 0.01)
                synthetic_data[symbol] = data
        else:
            synthetic_data = None
        
        # Test each indicator
        results = {}
        for indicator_name in self.optimized_indicators.keys():
            if synthetic_data:
                # Use synthetic data
                result = self.test_indicator_with_synthetic_data(indicator_name, synthetic_data)
            else:
                # Use real data
                result = self.test_indicator_accuracy(indicator_name, symbols)
            
            results[indicator_name] = result
        
        self.results = results
        return results
    
    def test_indicator_with_synthetic_data(self, indicator_name: str, synthetic_data: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Test indicator with synthetic data"""
        print(f"\nTesting {indicator_name} with synthetic data...")
        
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
            'avg_optimized_time': np.mean(execution_times_optimized),
            'avg_non_optimized_time': np.mean(execution_times_non_optimized),
            'speedup_factor': np.mean(execution_times_non_optimized) / np.mean(execution_times_optimized)
        }
    
    def create_visualization(self, save_path: str = "optimization_validation_results.png"):
        """Create comprehensive visualization of results"""
        if not self.results:
            print("No results to visualize. Run validation test first.")
            return
        
        # Set up the plot style
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Optimization Validation Results\nFisher Transform, CG Oscillator, RVI', fontsize=16, fontweight='bold')
        
        # Extract data for plotting
        indicators = list(self.results.keys())
        avg_errors = [self.results[ind]['avg_error_percentage'] for ind in indicators]
        max_errors = [self.results[ind]['max_error_percentage'] for ind in indicators]
        speedup_factors = [self.results[ind]['speedup_factor'] for ind in indicators]
        avg_optimized_times = [self.results[ind]['avg_optimized_time'] for ind in indicators]
        avg_non_optimized_times = [self.results[ind]['avg_non_optimized_time'] for ind in indicators]
        
        # Plot 1: Error Percentages
        x_pos = np.arange(len(indicators))
        width = 0.35
        
        axes[0, 0].bar(x_pos - width/2, avg_errors, width, label='Average Error %', alpha=0.8, color='skyblue')
        axes[0, 0].bar(x_pos + width/2, max_errors, width, label='Max Error %', alpha=0.8, color='lightcoral')
        axes[0, 0].set_xlabel('Indicators')
        axes[0, 0].set_ylabel('Error Percentage (%)')
        axes[0, 0].set_title('Accuracy Comparison: Error Percentages')
        axes[0, 0].set_xticks(x_pos)
        axes[0, 0].set_xticklabels([ind.replace('_', '\n') for ind in indicators], rotation=0)
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, (avg, max_err) in enumerate(zip(avg_errors, max_errors)):
            axes[0, 0].text(i - width/2, avg + 0.001, f'{avg:.4f}%', ha='center', va='bottom', fontsize=8)
            axes[0, 0].text(i + width/2, max_err + 0.001, f'{max_err:.4f}%', ha='center', va='bottom', fontsize=8)
        
        # Plot 2: Speedup Factors
        bars = axes[0, 1].bar(indicators, speedup_factors, alpha=0.8, color='lightgreen')
        axes[0, 1].set_xlabel('Indicators')
        axes[0, 1].set_ylabel('Speedup Factor (x)')
        axes[0, 1].set_title('Performance Improvement: Speedup Factors')
        axes[0, 1].set_xticklabels([ind.replace('_', '\n') for ind in indicators], rotation=0)
        axes[0, 1].grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, speedup in zip(bars, speedup_factors):
            axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                           f'{speedup:.1f}x', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Plot 3: Execution Time Comparison
        x_pos = np.arange(len(indicators))
        width = 0.35
        
        axes[1, 0].bar(x_pos - width/2, avg_optimized_times, width, label='Optimized', alpha=0.8, color='lightblue')
        axes[1, 0].bar(x_pos + width/2, avg_non_optimized_times, width, label='Non-Optimized', alpha=0.8, color='orange')
        axes[1, 0].set_xlabel('Indicators')
        axes[1, 0].set_ylabel('Execution Time (ms)')
        axes[1, 0].set_title('Performance Comparison: Execution Times')
        axes[1, 0].set_xticks(x_pos)
        axes[1, 0].set_xticklabels([ind.replace('_', '\n') for ind in indicators], rotation=0)
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_yscale('log')  # Log scale for better visualization
        
        # Plot 4: Summary Statistics
        summary_data = {
            'Metric': ['Avg Error %', 'Max Error %', 'Avg Speedup', 'Min Speedup', 'Max Speedup'],
            'Value': [
                f'{np.mean(avg_errors):.4f}%',
                f'{np.max(max_errors):.4f}%',
                f'{np.mean(speedup_factors):.1f}x',
                f'{np.min(speedup_factors):.1f}x',
                f'{np.max(speedup_factors):.1f}x'
            ]
        }
        
        axes[1, 1].axis('off')
        table_data = []
        for i, (metric, value) in enumerate(zip(summary_data['Metric'], summary_data['Value'])):
            table_data.append([metric, value])
        
        table = axes[1, 1].table(cellText=table_data,
                                colLabels=['Metric', 'Value'],
                                cellLoc='center',
                                loc='center',
                                bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 2)
        
        # Style the table
        for i in range(len(table_data) + 1):
            for j in range(2):
                cell = table[(i, j)]
                if i == 0:  # Header
                    cell.set_facecolor('#4CAF50')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    cell.set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')
        
        axes[1, 1].set_title('Summary Statistics', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {save_path}")
        plt.show()
    
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
            print(f"  Average Error: {result['avg_error_percentage']:.6f}%")
            print(f"  Maximum Error: {result['max_error_percentage']:.6f}%")
            print(f"  Average MSE: {result['avg_mse']:.8f}")
            print(f"  Average Optimized Time: {result['avg_optimized_time']:.3f}ms")
            print(f"  Average Non-Optimized Time: {result['avg_non_optimized_time']:.3f}ms")
            print(f"  Speedup Factor: {result['speedup_factor']:.1f}x")
        
        # Overall summary
        all_avg_errors = [result['avg_error_percentage'] for result in self.results.values()]
        all_max_errors = [result['max_error_percentage'] for result in self.results.values()]
        all_speedups = [result['speedup_factor'] for result in self.results.values()]
        
        print(f"\nOVERALL SUMMARY:")
        print(f"  Average Error Across All Indicators: {np.mean(all_avg_errors):.6f}%")
        print(f"  Maximum Error Across All Indicators: {np.max(all_max_errors):.6f}%")
        print(f"  Average Speedup Across All Indicators: {np.mean(all_speedups):.1f}x")
        print(f"  Minimum Speedup: {np.min(all_speedups):.1f}x")
        print(f"  Maximum Speedup: {np.max(all_speedups):.1f}x")
        
        # Validation conclusion
        max_error = np.max(all_max_errors)
        avg_speedup = np.mean(all_speedups)
        
        print(f"\nVALIDATION CONCLUSION:")
        if max_error < 0.001:  # Less than 0.001% error
            print(f"  ✅ EXCELLENT: Maximum error is {max_error:.6f}% (very low)")
        elif max_error < 0.01:  # Less than 0.01% error
            print(f"  ✅ GOOD: Maximum error is {max_error:.6f}% (low)")
        elif max_error < 0.1:  # Less than 0.1% error
            print(f"  ⚠️  ACCEPTABLE: Maximum error is {max_error:.6f}% (moderate)")
        else:
            print(f"  ❌ HIGH ERROR: Maximum error is {max_error:.6f}% (needs review)")
        
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
    
    # Create visualization
    validator.create_visualization()
    
    print("\nOptimization validation test completed!")

if __name__ == "__main__":
    main()
