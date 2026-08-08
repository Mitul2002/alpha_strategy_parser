#!/usr/bin/env python3
"""
Ehlers Trading Strategies
Using 9 optimized indicators and 3 transformations
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import time

from ehlers_indicators_optimized import (
    FisherTransform, InstantaneousTrendline, CGOscillator, RelativeVigorIndex,
    CyberCycleOscillator, Decycler, BandPassFilter, SuperSmoother, RoofingFilter
)
from ehlers_transformations import Stochasticization, Fisherization, CombinedTransformation

class EhlersStrategyEngine:
    """Engine for creating and testing Ehlers-based trading strategies"""
    
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
    
    def generate_test_data(self, length: int = 1000, trend: bool = True, noise: float = 0.1) -> np.ndarray:
        """Generate synthetic price data for testing"""
        # Base trend
        if trend:
            base_trend = np.linspace(100, 150, length)
        else:
            base_trend = np.full(length, 100)
        
        # Add cyclical component
        cycle = 10 * np.sin(np.linspace(0, 4*np.pi, length))
        
        # Add noise
        noise_component = noise * np.random.randn(length)
        
        # Combine components
        price_data = base_trend + cycle + noise_component
        
        return price_data
    
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
    
    def backtest_strategy(self, data: np.ndarray, signals: np.ndarray, **params) -> Dict[str, Any]:
        """Simple backtest of a strategy"""
        # Calculate returns
        returns = np.diff(data) / data[:-1]
        
        # Align signals with returns (signals are for next period)
        signal_returns = returns[signals[1:]]
        
        if len(signal_returns) == 0:
            return {
                'total_signals': 0,
                'win_rate': 0.0,
                'avg_return': 0.0,
                'total_return': 0.0,
                'sharpe_ratio': 0.0
            }
        
        # Calculate metrics
        total_signals = len(signal_returns)
        win_rate = np.mean(signal_returns > 0) * 100
        avg_return = np.mean(signal_returns) * 100
        total_return = np.sum(signal_returns) * 100
        sharpe_ratio = np.mean(signal_returns) / np.std(signal_returns) if np.std(signal_returns) > 0 else 0
        
        return {
            'total_signals': total_signals,
            'win_rate': win_rate,
            'avg_return': avg_return,
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio
        }
    
    def test_strategy(self, strategy_config: Dict[str, Any], data: np.ndarray = None) -> Dict[str, Any]:
        """Test a complete strategy"""
        if data is None:
            data = self.generate_test_data(1000)
        
        # Extract strategy parameters
        base_indicator = strategy_config.get('base_indicator', 'super_smoother')
        transformation = strategy_config.get('transformation', 'none')
        signal_type = strategy_config.get('signal_type', 'threshold')
        signal_params = strategy_config.get('signal_params', {})
        indicator_params = strategy_config.get('indicator_params', {})
        
        # Calculate enhanced indicator
        indicator_values = self.create_enhanced_indicator(
            base_indicator, transformation, data, **indicator_params
        )
        
        # Generate signals
        signals = self.generate_signals(indicator_values, signal_type, **signal_params)
        
        # Backtest
        backtest_results = self.backtest_strategy(data, signals)
        
        return {
            'strategy_config': strategy_config,
            'indicator_values': indicator_values,
            'signals': signals,
            'backtest_results': backtest_results,
            'data_length': len(data)
        }

def create_predefined_strategies() -> List[Dict[str, Any]]:
    """Create a set of predefined Ehlers strategies"""
    strategies = [
        # Strategy 1: SuperSmoother with Stochasticization
        {
            'name': 'SuperSmoother_Stochastic_Threshold',
            'base_indicator': 'super_smoother',
            'transformation': 'stochasticization',
            'signal_type': 'threshold',
            'signal_params': {'threshold': 50.0},
            'indicator_params': {'period': 10}
        },
        
        # Strategy 2: Fisher Transform with Zero Crossing
        {
            'name': 'Fisher_Zero_Cross',
            'base_indicator': 'fisher_transform',
            'transformation': 'none',
            'signal_type': 'zero_cross',
            'signal_params': {},
            'indicator_params': {'period': 10}
        },
        
        # Strategy 3: CG Oscillator with Fisherization
        {
            'name': 'CG_Oscillator_Fisher_Extreme',
            'base_indicator': 'cg_oscillator',
            'transformation': 'fisherization',
            'signal_type': 'extreme',
            'signal_params': {'percentile': 85},
            'indicator_params': {'period': 10}
        },
        
        # Strategy 4: Instantaneous Trendline with Crossover
        {
            'name': 'Instantaneous_Trend_Crossover',
            'base_indicator': 'instantaneous_trendline',
            'transformation': 'none',
            'signal_type': 'crossover',
            'signal_params': {},
            'indicator_params': {'alpha': 0.07}
        },
        
        # Strategy 5: RVI with Combined Transformation
        {
            'name': 'RVI_Combined_Threshold',
            'base_indicator': 'relative_vigor_index',
            'transformation': 'combined_transformation',
            'signal_type': 'threshold',
            'signal_params': {'threshold': 0.0},
            'indicator_params': {'period': 10}
        },
        
        # Strategy 6: Cyber Cycle with Stochasticization
        {
            'name': 'Cyber_Cycle_Stochastic_Extreme',
            'base_indicator': 'cyber_cycle_oscillator',
            'transformation': 'stochasticization',
            'signal_type': 'extreme',
            'signal_params': {'percentile': 80},
            'indicator_params': {'period': 10}
        },
        
        # Strategy 7: Decycler with Threshold
        {
            'name': 'Decycler_Threshold',
            'base_indicator': 'decycler',
            'transformation': 'none',
            'signal_type': 'threshold',
            'signal_params': {'threshold': 0.0},
            'indicator_params': {'cutoff_period': 40}
        },
        
        # Strategy 8: Band-Pass Filter with Fisherization
        {
            'name': 'BandPass_Fisher_Zero_Cross',
            'base_indicator': 'band_pass_filter',
            'transformation': 'fisherization',
            'signal_type': 'zero_cross',
            'signal_params': {},
            'indicator_params': {'low_period': 10, 'high_period': 20}
        },
        
        # Strategy 9: Roofing Filter with Combined Transformation
        {
            'name': 'Roofing_Combined_Crossover',
            'base_indicator': 'roofing_filter',
            'transformation': 'combined_transformation',
            'signal_type': 'crossover',
            'signal_params': {},
            'indicator_params': {'cutoff_period': 40}
        }
    ]
    
    return strategies

def run_strategy_comparison():
    """Run comparison of all predefined strategies"""
    print("EHLERS STRATEGIES COMPARISON")
    print("=" * 60)
    
    # Initialize engine
    engine = EhlersStrategyEngine()
    
    # Generate test data
    test_data = engine.generate_test_data(1000, trend=True, noise=0.05)
    print(f"Generated test data: {len(test_data)} points")
    print(f"Data range: [{test_data.min():.2f}, {test_data.max():.2f}]")
    
    # Get predefined strategies
    strategies = create_predefined_strategies()
    
    results = []
    
    for strategy_config in strategies:
        print(f"\n--- Testing {strategy_config['name']} ---")
        
        start_time = time.perf_counter()
        result = engine.test_strategy(strategy_config, test_data)
        end_time = time.perf_counter()
        
        execution_time = (end_time - start_time) * 1000
        backtest = result['backtest_results']
        
        print(f"  Execution time: {execution_time:.3f}ms")
        print(f"  Total signals: {backtest['total_signals']}")
        print(f"  Win rate: {backtest['win_rate']:.1f}%")
        print(f"  Avg return: {backtest['avg_return']:.3f}%")
        print(f"  Total return: {backtest['total_return']:.2f}%")
        print(f"  Sharpe ratio: {backtest['sharpe_ratio']:.3f}")
        
        results.append({
            'strategy_name': strategy_config['name'],
            'execution_time_ms': execution_time,
            'total_signals': backtest['total_signals'],
            'win_rate': backtest['win_rate'],
            'avg_return': backtest['avg_return'],
            'total_return': backtest['total_return'],
            'sharpe_ratio': backtest['sharpe_ratio']
        })
    
    # Summary
    print(f"\n{'='*60}")
    print("STRATEGY PERFORMANCE SUMMARY")
    print(f"{'='*60}")
    
    # Sort by Sharpe ratio
    results.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
    
    print(f"{'Rank':<4} {'Strategy':<30} {'Signals':<8} {'Win%':<6} {'Sharpe':<7} {'Time(ms)':<8}")
    print("-" * 70)
    
    for i, result in enumerate(results, 1):
        print(f"{i:<4} {result['strategy_name']:<30} {result['total_signals']:<8} "
              f"{result['win_rate']:<6.1f} {result['sharpe_ratio']:<7.3f} {result['execution_time_ms']:<8.1f}")
    
    return results

if __name__ == "__main__":
    results = run_strategy_comparison()
