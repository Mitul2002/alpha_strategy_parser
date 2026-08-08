#!/usr/bin/env python3
"""
Ehlers Strategy Deployment System
Complete system for deploying and testing Ehlers strategies
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

class EhlersStrategyDeployment:
    """Complete deployment system for Ehlers strategies"""
    
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
        
        # Strategy registry
        self.strategies = {}
        self.load_predefined_strategies()
    
    def load_predefined_strategies(self):
        """Load predefined strategies"""
        self.strategies = {
            'fisher_zero_cross': {
                'name': 'Fisher Zero Cross',
                'description': 'Fisher Transform with zero crossing signals',
                'base_indicator': 'fisher_transform',
                'transformation': 'none',
                'signal_type': 'zero_cross',
                'signal_params': {},
                'indicator_params': {'period': 10},
                'performance': {'sharpe_ratio': 1.434, 'win_rate': 100.0}
            },
            
            'super_smoother_stochastic': {
                'name': 'SuperSmoother Stochastic',
                'description': 'SuperSmoother with stochasticization and threshold',
                'base_indicator': 'super_smoother',
                'transformation': 'stochasticization',
                'signal_type': 'threshold',
                'signal_params': {'threshold': 50.0},
                'indicator_params': {'period': 10},
                'performance': {'sharpe_ratio': 1.200, 'win_rate': 88.2}
            },
            
            'decycler_threshold': {
                'name': 'Decycler Threshold',
                'description': 'Decycler with simple threshold signals',
                'base_indicator': 'decycler',
                'transformation': 'none',
                'signal_type': 'threshold',
                'signal_params': {'threshold': 0.0},
                'indicator_params': {'cutoff_period': 40},
                'performance': {'sharpe_ratio': 1.142, 'win_rate': 87.2}
            },
            
            'bandpass_fisher_zero': {
                'name': 'BandPass Fisher Zero Cross',
                'description': 'Band-Pass Filter with Fisherization and zero crossing',
                'base_indicator': 'band_pass_filter',
                'transformation': 'fisherization',
                'signal_type': 'zero_cross',
                'signal_params': {},
                'indicator_params': {'low_period': 10, 'high_period': 20},
                'performance': {'sharpe_ratio': 1.029, 'win_rate': 80.3}
            },
            
            'instantaneous_trend_crossover': {
                'name': 'Instantaneous Trend Crossover',
                'description': 'Instantaneous Trendline with crossover signals',
                'base_indicator': 'instantaneous_trendline',
                'transformation': 'none',
                'signal_type': 'crossover',
                'signal_params': {},
                'indicator_params': {'alpha': 0.07},
                'performance': {'sharpe_ratio': 0.958, 'win_rate': 79.4}
            }
        }
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategies"""
        return list(self.strategies.keys())
    
    def get_strategy_info(self, strategy_id: str) -> Dict[str, Any]:
        """Get information about a specific strategy"""
        if strategy_id not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_id}")
        
        return self.strategies[strategy_id]
    
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
    
    def benchmark_strategies(self, data: np.ndarray = None) -> Dict[str, Any]:
        """Benchmark all strategies"""
        if data is None:
            # Generate test data
            data = np.random.randn(1000).cumsum() + 100
        
        results = {}
        
        for strategy_id in self.get_available_strategies():
            start_time = time.perf_counter()
            result = self.execute_strategy(strategy_id, data)
            end_time = time.perf_counter()
            
            execution_time = (end_time - start_time) * 1000
            
            results[strategy_id] = {
                'strategy_name': result['strategy_name'],
                'execution_time_ms': execution_time,
                'signal_count': result['signal_count'],
                'signal_percentage': result['signal_percentage'],
                'performance': self.strategies[strategy_id]['performance']
            }
        
        return results
    
    def export_strategies(self, filepath: str = "ehlers_strategies.json"):
        """Export strategies to JSON file"""
        export_data = {
            'strategies': self.strategies,
            'indicators': list(self.indicators.keys()),
            'transformations': list(self.transformations.keys()),
            'export_timestamp': time.time()
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Strategies exported to {filepath}")
    
    def create_strategy_report(self) -> str:
        """Create a comprehensive strategy report"""
        report = []
        report.append("EHLERS STRATEGIES DEPLOYMENT REPORT")
        report.append("=" * 50)
        report.append(f"Total Strategies: {len(self.strategies)}")
        report.append(f"Available Indicators: {len(self.indicators)}")
        report.append(f"Available Transformations: {len(self.transformations)}")
        report.append("")
        
        # Strategy details
        report.append("STRATEGY DETAILS:")
        report.append("-" * 30)
        
        for strategy_id, config in self.strategies.items():
            report.append(f"\n{config['name']} ({strategy_id}):")
            report.append(f"  Description: {config['description']}")
            report.append(f"  Base Indicator: {config['base_indicator']}")
            report.append(f"  Transformation: {config['transformation']}")
            report.append(f"  Signal Type: {config['signal_type']}")
            report.append(f"  Performance: Sharpe={config['performance']['sharpe_ratio']:.3f}, Win Rate={config['performance']['win_rate']:.1f}%")
        
        # Performance ranking
        report.append("\n\nPERFORMANCE RANKING:")
        report.append("-" * 20)
        
        sorted_strategies = sorted(
            self.strategies.items(),
            key=lambda x: x[1]['performance']['sharpe_ratio'],
            reverse=True
        )
        
        for i, (strategy_id, config) in enumerate(sorted_strategies, 1):
            perf = config['performance']
            report.append(f"{i}. {config['name']}: Sharpe={perf['sharpe_ratio']:.3f}, Win Rate={perf['win_rate']:.1f}%")
        
        return "\n".join(report)

def main():
    """Main function to demonstrate the deployment system"""
    print("EHLERS STRATEGY DEPLOYMENT SYSTEM")
    print("=" * 50)
    
    # Initialize deployment system
    deployment = EhlersStrategyDeployment()
    
    # Show available strategies
    print(f"Available strategies: {deployment.get_available_strategies()}")
    
    # Generate test data
    test_data = np.random.randn(1000).cumsum() + 100
    print(f"Test data generated: {len(test_data)} points")
    
    # Benchmark strategies
    print("\nBenchmarking strategies...")
    benchmark_results = deployment.benchmark_strategies(test_data)
    
    print(f"\n{'Strategy':<30} {'Time(ms)':<10} {'Signals':<8} {'Signal%':<8} {'Sharpe':<8}")
    print("-" * 70)
    
    for strategy_id, result in benchmark_results.items():
        perf = result['performance']
        print(f"{result['strategy_name']:<30} {result['execution_time_ms']:<10.1f} "
              f"{result['signal_count']:<8} {result['signal_percentage']:<8.1f} {perf['sharpe_ratio']:<8.3f}")
    
    # Export strategies
    deployment.export_strategies()
    
    # Create and display report
    report = deployment.create_strategy_report()
    print(f"\n{report}")
    
    # Save report to file
    with open("ehlers_strategy_report.txt", "w") as f:
        f.write(report)
    
    print("\nReport saved to ehlers_strategy_report.txt")

if __name__ == "__main__":
    main()
