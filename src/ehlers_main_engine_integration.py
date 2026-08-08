#!/usr/bin/env python3
"""
Ehlers Main Engine Integration
Integrate Ehlers indicators and 50 strategies into the main alpha strategy parser engine
"""

import sys
import os
import time
import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from ehlers_indicators import (
    FisherTransform, InstantaneousTrendline, CGOscillator, RelativeVigorIndex,
    CyberCycleOscillator, Decycler, BandPassFilter, SuperSmoother, RoofingFilter
)
from ehlers_transformations import Stochasticization, Fisherization, CombinedTransformation

class EhlersMainEngine:
    """Main engine integration for Ehlers indicators and strategies"""
    
    def __init__(self, data_path: str = None):
        self.data_path = data_path or "../context/rsi_forward_returns/data_partitioned"
        
        # Initialize Ehlers indicators
        self.ehlers_indicators = {
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
        self.ehlers_transformations = {
            'stochasticization': Stochasticization(10),
            'fisherization': Fisherization(10),
            'combined_transformation': CombinedTransformation(10)
        }
        
        # Load 50 strategies
        self.strategies = self.load_50_strategies()
        
        self.logger = logging.getLogger(__name__)
    
    def load_50_strategies(self) -> Dict[str, Any]:
        """Load the 50 Ehlers strategies"""
        try:
            with open('ehlers_50_strategies.json', 'r') as f:
                data = json.load(f)
                return data['strategies']
        except FileNotFoundError:
            print("ehlers_50_strategies.json not found. Creating default strategies...")
            return self.create_default_strategies()
    
    def create_default_strategies(self) -> Dict[str, Any]:
        """Create default strategies if JSON file not found"""
        return {
            'strategy_01': {
                'name': 'Fisher Transform Base',
                'base_indicator': 'fisher_transform',
                'transformation': 'none',
                'signal_type': 'threshold',
                'signal_params': {'threshold': 0.0},
                'indicator_params': {'period': 10}
            },
            'strategy_02': {
                'name': 'SuperSmoother Stochastic',
                'base_indicator': 'super_smoother',
                'transformation': 'stochasticization',
                'signal_type': 'threshold',
                'signal_params': {'threshold': 50.0},
                'indicator_params': {'period': 10}
            }
        }
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols from data directory"""
        symbols = []
        data_path = Path(self.data_path)
        
        if data_path.exists():
            for file_path in data_path.glob("symbol=*/"):
                symbol = file_path.name.replace("symbol=", "")
                symbols.append(symbol)
        
        return sorted(symbols)
    
    def load_symbol_data(self, symbol: str) -> Optional[Dict[str, np.ndarray]]:
        """Load OHLCV data for a symbol"""
        try:
            data_path = Path(self.data_path) / f"symbol={symbol}"
            parquet_file = data_path / f"symbol={symbol}.parquet"
            
            if not parquet_file.exists():
                return None
            
            # Load data using pandas
            df = pd.read_parquet(parquet_file)
            
            # Convert to numpy arrays
            data = {
                'open': df['open'].values,
                'high': df['high'].values,
                'low': df['low'].values,
                'close': df['close'].values,
                'volume': df['volume'].values if 'volume' in df.columns else None
            }
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading data for {symbol}: {e}")
            return None
    
    def calculate_ehlers_indicator(self, indicator_name: str, data: np.ndarray, **params) -> np.ndarray:
        """Calculate a specific Ehlers indicator"""
        if indicator_name not in self.ehlers_indicators:
            raise ValueError(f"Unknown Ehlers indicator: {indicator_name}")
        
        indicator = self.ehlers_indicators[indicator_name]
        return indicator.calculate(data, **params)
    
    def apply_ehlers_transformation(self, transformation_name: str, data: np.ndarray, **params) -> np.ndarray:
        """Apply a specific Ehlers transformation"""
        if transformation_name not in self.ehlers_transformations:
            raise ValueError(f"Unknown Ehlers transformation: {transformation_name}")
        
        transformation = self.ehlers_transformations[transformation_name]
        return transformation.apply(data, **params)
    
    def get_enhanced_indicator(self, base_indicator: str, transformation: str, data: np.ndarray, **params) -> np.ndarray:
        """Get an enhanced indicator (base + transformation)"""
        # Calculate base indicator
        base_result = self.calculate_ehlers_indicator(base_indicator, data, **params)
        
        # Apply transformation
        if transformation == 'none':
            return base_result
        else:
            return self.apply_ehlers_transformation(transformation, base_result, **params)
    
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
    
    def execute_ehlers_strategy(self, strategy_id: str, symbols: List[str] = None) -> Dict[str, Any]:
        """Execute a specific Ehlers strategy"""
        if strategy_id not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_id}")
        
        if symbols is None:
            symbols = self.get_available_symbols()[:10]  # Limit to first 10 for testing
        
        strategy_config = self.strategies[strategy_id]
        
        results = {
            'strategy_id': strategy_id,
            'strategy_name': strategy_config['name'],
            'symbols_processed': 0,
            'total_signals': 0,
            'execution_time': 0,
            'symbol_results': {},
            'performance_metrics': {}
        }
        
        start_time = time.time()
        
        # Extract strategy configuration
        base_indicator = strategy_config['base_indicator']
        transformation = strategy_config['transformation']
        signal_type = strategy_config['signal_type']
        signal_params = strategy_config['signal_params']
        indicator_params = strategy_config['indicator_params']
        
        # Process each symbol
        for symbol in symbols:
            data = self.load_symbol_data(symbol)
            if data is None:
                continue
            
            try:
                # Calculate enhanced indicator
                indicator_values = self.get_enhanced_indicator(
                    base_indicator, transformation, data['close'], **indicator_params
                )
                
                # Generate signals
                signals = self.generate_signals(indicator_values, signal_type, **signal_params)
                signal_count = np.sum(signals)
                
                if signal_count > 0:
                    # Calculate basic metrics
                    symbol_metrics = {
                        'symbol': symbol,
                        'total_signals': int(signal_count),
                        'signal_percentage': float(signal_count / len(signals) * 100),
                        'avg_indicator_value': float(np.nanmean(indicator_values)),
                        'indicator_std': float(np.nanstd(indicator_values)),
                        'data_length': len(data['close'])
                    }
                    
                    results['symbol_results'][symbol] = symbol_metrics
                
                results['symbols_processed'] += 1
                results['total_signals'] += signal_count
                
            except Exception as e:
                self.logger.error(f"Error processing {symbol}: {e}")
                continue
        
        results['execution_time'] = time.time() - start_time
        
        # Calculate performance metrics
        if results['symbols_processed'] > 0:
            results['performance_metrics'] = {
                'symbols_per_second': results['symbols_processed'] / results['execution_time'],
                'signals_per_second': results['total_signals'] / results['execution_time'],
                'avg_signals_per_symbol': results['total_signals'] / results['symbols_processed']
            }
        
        return results
    
    def benchmark_all_strategies(self, num_symbols: int = 5) -> Dict[str, Any]:
        """Benchmark all 50 strategies"""
        symbols = self.get_available_symbols()[:num_symbols]
        
        if len(symbols) == 0:
            print("No real symbols found, using synthetic data...")
            return self.benchmark_with_synthetic_data()
        
        results = {}
        
        for strategy_id in self.strategies.keys():
            print(f"Benchmarking {strategy_id}...")
            result = self.execute_ehlers_strategy(strategy_id, symbols)
            results[strategy_id] = result
        
        return results
    
    def benchmark_with_synthetic_data(self) -> Dict[str, Any]:
        """Benchmark with synthetic data when real data is not available"""
        # Generate synthetic data
        synthetic_data = np.random.randn(1000).cumsum() + 100
        
        results = {}
        
        for strategy_id, strategy_config in self.strategies.items():
            print(f"Benchmarking {strategy_id} with synthetic data...")
            
            start_time = time.perf_counter()
            
            # Extract strategy configuration
            base_indicator = strategy_config['base_indicator']
            transformation = strategy_config['transformation']
            signal_type = strategy_config['signal_type']
            signal_params = strategy_config['signal_params']
            indicator_params = strategy_config['indicator_params']
            
            # Calculate enhanced indicator
            indicator_values = self.get_enhanced_indicator(
                base_indicator, transformation, synthetic_data, **indicator_params
            )
            
            # Generate signals
            signals = self.generate_signals(indicator_values, signal_type, **signal_params)
            signal_count = np.sum(signals)
            
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000
            
            results[strategy_id] = {
                'strategy_name': strategy_config['name'],
                'execution_time_ms': execution_time,
                'signal_count': int(signal_count),
                'signal_percentage': float(signal_count / len(signals) * 100),
                'data_length': len(synthetic_data)
            }
        
        return results
    
    def get_available_indicators(self) -> List[str]:
        """Get list of available Ehlers indicators"""
        return list(self.ehlers_indicators.keys())
    
    def get_available_transformations(self) -> List[str]:
        """Get list of available transformations"""
        return ['none'] + list(self.ehlers_transformations.keys())
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategies"""
        return list(self.strategies.keys())
    
    def create_integration_report(self) -> str:
        """Create integration report"""
        report = []
        report.append("EHLERS MAIN ENGINE INTEGRATION REPORT")
        report.append("=" * 50)
        report.append(f"Ehlers Indicators: {len(self.ehlers_indicators)}")
        report.append(f"Transformations: {len(self.ehlers_transformations)}")
        report.append(f"Strategies: {len(self.strategies)}")
        report.append(f"Available Symbols: {len(self.get_available_symbols())}")
        report.append("")
        
        # List indicators
        report.append("Available Ehlers Indicators:")
        for indicator in self.ehlers_indicators.keys():
            report.append(f"  - {indicator}")
        report.append("")
        
        # List transformations
        report.append("Available Transformations:")
        for transformation in self.ehlers_transformations.keys():
            report.append(f"  - {transformation}")
        report.append("")
        
        # List strategy categories
        report.append("Strategy Categories:")
        categories = {
            'Base Indicators (1-9)': list(range(1, 10)),
            'Stochasticized (10-18)': list(range(10, 19)),
            'Fisherized (19-27)': list(range(19, 28)),
            'Combined Transform (28-36)': list(range(28, 37)),
            'Extreme Signals (37-45)': list(range(37, 46)),
            'Special Combinations (46-50)': list(range(46, 51))
        }
        
        for category, strategy_nums in categories.items():
            report.append(f"  {category}: {len(strategy_nums)} strategies")
        
        return "\n".join(report)

def main():
    """Main function to test the integrated engine"""
    print("Ehlers Main Engine Integration Test")
    print("=" * 50)
    
    # Initialize engine
    engine = EhlersMainEngine()
    
    # Show integration status
    print(f"Ehlers Indicators: {len(engine.get_available_indicators())}")
    print(f"Transformations: {len(engine.get_available_transformations())}")
    print(f"Strategies: {len(engine.get_available_strategies())}")
    print(f"Available Symbols: {len(engine.get_available_symbols())}")
    
    # Test individual indicators
    print("\nTesting individual indicators...")
    test_data = np.random.randn(1000).cumsum() + 100
    
    for indicator_name in engine.get_available_indicators():
        start_time = time.perf_counter()
        result = engine.calculate_ehlers_indicator(indicator_name, test_data)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        print(f"  {indicator_name}: {execution_time:.3f}ms")
    
    # Test transformations
    print("\nTesting transformations...")
    for transformation_name in engine.get_available_transformations():
        if transformation_name != 'none':
            start_time = time.perf_counter()
            result = engine.apply_ehlers_transformation(transformation_name, test_data)
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000
            print(f"  {transformation_name}: {execution_time:.3f}ms")
    
    # Benchmark strategies
    print("\nBenchmarking strategies...")
    benchmark_results = engine.benchmark_all_strategies(num_symbols=3)
    
    # Show performance summary
    execution_times = [result['execution_time_ms'] for result in benchmark_results.values()]
    signal_counts = [result['signal_count'] for result in benchmark_results.values()]
    
    print(f"\nPerformance Summary:")
    print(f"  Strategies tested: {len(benchmark_results)}")
    print(f"  Average execution time: {np.mean(execution_times):.3f}ms")
    print(f"  Fastest strategy: {min(execution_times):.3f}ms")
    print(f"  Slowest strategy: {max(execution_times):.3f}ms")
    print(f"  Average signals: {np.mean(signal_counts):.0f}")
    
    # Create integration report
    report = engine.create_integration_report()
    print(f"\n{report}")
    
    # Save report
    with open("ehlers_main_engine_integration_report.txt", "w") as f:
        f.write(report)
    
    print("\nEhlers main engine integration test completed!")

if __name__ == "__main__":
    main()
