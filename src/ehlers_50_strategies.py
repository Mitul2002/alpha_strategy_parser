#!/usr/bin/env python3
"""
Ehlers 50 Varied Strategies
Create 50 diverse strategies by combining 9 Ehlers indicators and 3 transformations
"""

import numpy as np
import pandas as pd
import json
import time
from typing import Dict, List, Any, Tuple
from pathlib import Path

from ehlers_indicators import (
    FisherTransform, InstantaneousTrendline, CGOscillator, RelativeVigorIndex,
    CyberCycleOscillator, Decycler, BandPassFilter, SuperSmoother, RoofingFilter
)
from ehlers_transformations import Stochasticization, Fisherization, CombinedTransformation

class Ehlers50Strategies:
    """Create 50 varied strategies using Ehlers indicators and transformations"""
    
    def __init__(self):
        # Initialize indicators
        self.indicators = {
            'fisher_transform': FisherTransform(10),
            'instantaneous_trendline': InstantaneousTrendline(0.07),
            'cg_oscillator': CGOscillator(10),
            'relative_vigor_index': RelativeVigorIndex(10),
            'cyber_cycle_oscillator': CyberCycleOscillator(10),
            'decycler': Decycler(40),
            'band_pass_filter': BandPassFilter(10, 20),
            'super_smoother': SuperSmoother(10),
            'roofing_filter': RoofingFilter(40)
        }
        
        # Initialize transformations
        self.transformations = {
            'stochasticization': Stochasticization(10),
            'fisherization': Fisherization(10),
            'combined_transformation': CombinedTransformation(10)
        }
        
        # Strategy configurations
        self.strategies = {}
        self.create_50_strategies()
    
    def create_50_strategies(self):
        """Create 50 varied strategies"""
        
        # Strategy 1-9: Base indicators with no transformation
        base_indicators = list(self.indicators.keys())
        for i, indicator in enumerate(base_indicators, 1):
            self.strategies[f'strategy_{i:02d}'] = {
                'name': f'{indicator.replace("_", " ").title()} Base',
                'description': f'Base {indicator} with threshold signals',
                'base_indicator': indicator,
                'transformation': 'none',
                'signal_type': 'threshold',
                'signal_params': {'threshold': 0.0},
                'indicator_params': self.get_default_params(indicator)
            }
        
        # Strategy 10-18: Base indicators with stochasticization
        for i, indicator in enumerate(base_indicators, 10):
            self.strategies[f'strategy_{i:02d}'] = {
                'name': f'{indicator.replace("_", " ").title()} Stochastic',
                'description': f'{indicator} with stochasticization and threshold',
                'base_indicator': indicator,
                'transformation': 'stochasticization',
                'signal_type': 'threshold',
                'signal_params': {'threshold': 50.0},
                'indicator_params': self.get_default_params(indicator)
            }
        
        # Strategy 19-27: Base indicators with fisherization
        for i, indicator in enumerate(base_indicators, 19):
            self.strategies[f'strategy_{i:02d}'] = {
                'name': f'{indicator.replace("_", " ").title()} Fisher',
                'description': f'{indicator} with fisherization and zero cross',
                'base_indicator': indicator,
                'transformation': 'fisherization',
                'signal_type': 'zero_cross',
                'signal_params': {},
                'indicator_params': self.get_default_params(indicator)
            }
        
        # Strategy 28-36: Base indicators with combined transformation
        for i, indicator in enumerate(base_indicators, 28):
            self.strategies[f'strategy_{i:02d}'] = {
                'name': f'{indicator.replace("_", " ").title()} Combined',
                'description': f'{indicator} with combined transformation and crossover',
                'base_indicator': indicator,
                'transformation': 'combined_transformation',
                'signal_type': 'crossover',
                'signal_params': {},
                'indicator_params': self.get_default_params(indicator)
            }
        
        # Strategy 37-45: Fast indicators with extreme signals
        fast_indicators = ['instantaneous_trendline', 'decycler', 'band_pass_filter', 'super_smoother', 'roofing_filter', 'cg_oscillator', 'cyber_cycle_oscillator', 'relative_vigor_index', 'fisher_transform']
        for i, indicator in enumerate(fast_indicators, 37):
            self.strategies[f'strategy_{i:02d}'] = {
                'name': f'{indicator.replace("_", " ").title()} Extreme',
                'description': f'{indicator} with extreme value signals',
                'base_indicator': indicator,
                'transformation': 'stochasticization',
                'signal_type': 'extreme',
                'signal_params': {'percentile': 85},
                'indicator_params': self.get_default_params(indicator)
            }
        
        # Strategy 46-50: Special combinations
        special_combinations = [
            {
                'name': 'Fisher SuperSmoother Hybrid',
                'description': 'Fisher Transform with SuperSmoother stochasticization',
                'base_indicator': 'fisher_transform',
                'transformation': 'stochasticization',
                'signal_type': 'threshold',
                'signal_params': {'threshold': 50.0},
                'indicator_params': {'period': 15}
            },
            {
                'name': 'CG Oscillator Enhanced',
                'description': 'CG Oscillator with combined transformation',
                'base_indicator': 'cg_oscillator',
                'transformation': 'combined_transformation',
                'signal_type': 'extreme',
                'signal_params': {'percentile': 80},
                'indicator_params': {'period': 20}
            },
            {
                'name': 'Instantaneous Trend Advanced',
                'description': 'Instantaneous Trendline with fisherization',
                'base_indicator': 'instantaneous_trendline',
                'transformation': 'fisherization',
                'signal_type': 'zero_cross',
                'signal_params': {},
                'indicator_params': {'alpha': 0.05}
            },
            {
                'name': 'RVI Stochastic Enhanced',
                'description': 'RVI with stochasticization and extreme signals',
                'base_indicator': 'relative_vigor_index',
                'transformation': 'stochasticization',
                'signal_type': 'extreme',
                'signal_params': {'percentile': 90},
                'indicator_params': {'period': 15}
            },
            {
                'name': 'Cyber Cycle Ultimate',
                'description': 'Cyber Cycle with combined transformation and crossover',
                'base_indicator': 'cyber_cycle_oscillator',
                'transformation': 'combined_transformation',
                'signal_type': 'crossover',
                'signal_params': {},
                'indicator_params': {'period': 15}
            }
        ]
        
        for i, config in enumerate(special_combinations, 46):
            self.strategies[f'strategy_{i:02d}'] = config
    
    def get_default_params(self, indicator: str) -> Dict[str, Any]:
        """Get default parameters for an indicator"""
        defaults = {
            'fisher_transform': {'period': 10},
            'instantaneous_trendline': {'alpha': 0.07},
            'cg_oscillator': {'period': 10},
            'relative_vigor_index': {'period': 10},
            'cyber_cycle_oscillator': {'period': 10},
            'decycler': {'cutoff_period': 40},
            'band_pass_filter': {'low_period': 10, 'high_period': 20},
            'super_smoother': {'period': 10},
            'roofing_filter': {'cutoff_period': 40}
        }
        return defaults.get(indicator, {})
    
    def calculate_indicator(self, indicator_name: str, data: np.ndarray, **params) -> np.ndarray:
        """Calculate a specific indicator"""
        if indicator_name not in self.indicators:
            raise ValueError(f"Unknown indicator: {indicator_name}")
        
        return self.indicators[indicator_name].calculate(data, **params)
    
    def apply_transformation(self, transformation_name: str, data: np.ndarray, **params) -> np.ndarray:
        """Apply a transformation to data"""
        if transformation_name not in self.transformations:
            raise ValueError(f"Unknown transformation: {transformation_name}")
        
        return self.transformations[transformation_name].apply(data, **params)
    
    def create_enhanced_indicator(self, base_indicator: str, transformation: str, data: np.ndarray, **params) -> np.ndarray:
        """Create an enhanced indicator (base + transformation)"""
        # Calculate base indicator
        base_result = self.calculate_indicator(base_indicator, data, **params)
        
        # Apply transformation
        if transformation == 'none':
            return base_result
        else:
            return self.apply_transformation(transformation, base_result, **params)
    
    def generate_signals(self, indicator_values: np.ndarray, signal_type: str = 'threshold', **params) -> np.ndarray:
        """Generate trading signals from indicator values"""
        signals = np.zeros_like(indicator_values, dtype=bool)
        
        if signal_type == 'threshold':
            threshold = params.get('threshold', 0.0)
            signals = indicator_values > threshold
        
        elif signal_type == 'crossover':
            # Simple crossover with previous value
            signals[1:] = (indicator_values[1:] > indicator_values[:-1])
        
        elif signal_type == 'zero_cross':
            # Zero crossing
            signals[1:] = (indicator_values[1:] > 0) & (indicator_values[:-1] <= 0)
        
        elif signal_type == 'extreme':
            # Extreme values (top/bottom percentiles)
            percentile = params.get('percentile', 90)
            upper_threshold = np.nanpercentile(indicator_values, percentile)
            lower_threshold = np.nanpercentile(indicator_values, 100 - percentile)
            signals = (indicator_values > upper_threshold) | (indicator_values < lower_threshold)
        
        return signals
    
    def execute_strategy(self, strategy_id: str, data: np.ndarray) -> Dict[str, Any]:
        """Execute a specific strategy"""
        if strategy_id not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_id}")
        
        strategy_config = self.strategies[strategy_id]
        
        # Extract parameters
        base_indicator = strategy_config['base_indicator']
        transformation = strategy_config['transformation']
        signal_type = strategy_config['signal_type']
        signal_params = strategy_config['signal_params']
        indicator_params = strategy_config['indicator_params']
        
        # Calculate enhanced indicator
        indicator_values = self.create_enhanced_indicator(
            base_indicator, transformation, data, **indicator_params
        )
        
        # Generate signals
        signals = self.generate_signals(indicator_values, signal_type, **signal_params)
        
        return {
            'strategy_id': strategy_id,
            'strategy_name': strategy_config['name'],
            'indicator_values': indicator_values,
            'signals': signals,
            'signal_count': np.sum(signals),
            'signal_percentage': np.sum(signals) / len(signals) * 100
        }
    
    def benchmark_all_strategies(self, data: np.ndarray = None) -> Dict[str, Any]:
        """Benchmark all 50 strategies"""
        if data is None:
            # Generate test data
            data = np.random.randn(1000).cumsum() + 100
        
        results = {}
        
        for strategy_id in self.strategies.keys():
            start_time = time.perf_counter()
            result = self.execute_strategy(strategy_id, data)
            end_time = time.perf_counter()
            
            execution_time = (end_time - start_time) * 1000
            
            results[strategy_id] = {
                'strategy_name': result['strategy_name'],
                'execution_time_ms': execution_time,
                'signal_count': result['signal_count'],
                'signal_percentage': result['signal_percentage']
            }
        
        return results
    
    def export_strategies(self, filepath: str = "ehlers_50_strategies.json"):
        """Export all 50 strategies to JSON file"""
        export_data = {
            'strategies': self.strategies,
            'indicators': list(self.indicators.keys()),
            'transformations': list(self.transformations.keys()),
            'total_strategies': len(self.strategies),
            'export_timestamp': time.time()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"50 strategies exported to {filepath}")
    
    def create_strategy_report(self) -> str:
        """Create a comprehensive strategy report"""
        report = []
        report.append("EHLERS 50 STRATEGIES REPORT")
        report.append("=" * 50)
        report.append(f"Total Strategies: {len(self.strategies)}")
        report.append(f"Available Indicators: {len(self.indicators)}")
        report.append(f"Available Transformations: {len(self.transformations)}")
        report.append("")
        
        # Strategy categories
        categories = {
            'Base Indicators (1-9)': list(range(1, 10)),
            'Stochasticized (10-18)': list(range(10, 19)),
            'Fisherized (19-27)': list(range(19, 28)),
            'Combined Transform (28-36)': list(range(28, 37)),
            'Extreme Signals (37-45)': list(range(37, 46)),
            'Special Combinations (46-50)': list(range(46, 51))
        }
        
        for category, strategy_nums in categories.items():
            report.append(f"{category}:")
            for num in strategy_nums:
                strategy_id = f'strategy_{num:02d}'
                if strategy_id in self.strategies:
                    config = self.strategies[strategy_id]
                    report.append(f"  {num:2d}. {config['name']}")
            report.append("")
        
        return "\n".join(report)

def main():
    """Main function to create and test 50 strategies"""
    print("Creating 50 Ehlers Strategies...")
    
    # Initialize strategy creator
    strategy_creator = Ehlers50Strategies()
    
    # Show strategy count
    print(f"Created {len(strategy_creator.strategies)} strategies")
    
    # Generate test data
    test_data = np.random.randn(1000).cumsum() + 100
    print(f"Generated test data: {len(test_data)} points")
    
    # Benchmark strategies
    print("\nBenchmarking all strategies...")
    benchmark_results = strategy_creator.benchmark_all_strategies(test_data)
    
    # Show performance summary
    execution_times = [result['execution_time_ms'] for result in benchmark_results.values()]
    signal_counts = [result['signal_count'] for result in benchmark_results.values()]
    
    print(f"\nPerformance Summary:")
    print(f"  Average execution time: {np.mean(execution_times):.3f}ms")
    print(f"  Fastest strategy: {min(execution_times):.3f}ms")
    print(f"  Slowest strategy: {max(execution_times):.3f}ms")
    print(f"  Average signals: {np.mean(signal_counts):.0f}")
    print(f"  Total strategies: {len(benchmark_results)}")
    
    # Export strategies
    strategy_creator.export_strategies()
    
    # Create and display report
    report = strategy_creator.create_strategy_report()
    print(f"\n{report}")
    
    # Save report to file
    with open("ehlers_50_strategies_report.txt", "w") as f:
        f.write(report)
    
    print("\n50 strategies created and tested successfully!")

if __name__ == "__main__":
    main()
