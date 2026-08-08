#!/usr/bin/env python3
"""
Ehlers Backend Integration
Integrates Ehlers indicators with the existing alpha strategy parser backend
"""

import sys
import os
import time
import numpy as np
import pandas as pd
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

class EhlersBackend:
    """Backend that integrates Ehlers indicators with existing strategy parser"""
    
    def __init__(self, data_path: str = None):
        self.data_path = data_path or "context/rsi_forward_returns/data_partitioned"
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
        
        self.ehlers_transformations = {
            'stochasticization': Stochasticization(10),
            'fisherization': Fisherization(10),
            'combined_transformation': CombinedTransformation(10)
        }
        
        self.logger = logging.getLogger(__name__)
    
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
            
            # Load data using pandas (fallback from polars)
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
    
    def execute_ehlers_strategy(self, strategy_config: Dict[str, Any], symbols: List[str] = None) -> Dict[str, Any]:
        """Execute a strategy using Ehlers indicators"""
        if symbols is None:
            symbols = self.get_available_symbols()
        
        results = {
            'strategy_config': strategy_config,
            'symbols_processed': 0,
            'total_signals': 0,
            'execution_time': 0,
            'symbol_results': {},
            'performance_metrics': {}
        }
        
        start_time = time.time()
        
        # Extract strategy configuration
        base_indicator = strategy_config.get('base_indicator', 'super_smoother')
        transformation = strategy_config.get('transformation', 'none')
        signal_threshold = strategy_config.get('signal_threshold', 0.0)
        lookback_period = strategy_config.get('lookback_period', 20)
        
        # Process each symbol
        for symbol in symbols[:10]:  # Limit to first 10 for testing
            data = self.load_symbol_data(symbol)
            if data is None:
                continue
            
            try:
                # Calculate enhanced indicator
                indicator_values = self.get_enhanced_indicator(
                    base_indicator, transformation, data['close']
                )
                
                # Generate signals based on threshold
                signals = indicator_values > signal_threshold
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
    
    def get_available_indicators(self) -> List[str]:
        """Get list of available Ehlers indicators"""
        return list(self.ehlers_indicators.keys())
    
    def get_available_transformations(self) -> List[str]:
        """Get list of available transformations"""
        return ['none'] + list(self.ehlers_transformations.keys())
    
    def benchmark_ehlers_indicators(self, data_size: int = 1000) -> Dict[str, Any]:
        """Benchmark all Ehlers indicators"""
        # Generate test data
        test_data = np.random.randn(data_size).cumsum() + 100
        
        results = {}
        
        for name, indicator in self.ehlers_indicators.items():
            start_time = time.perf_counter()
            result = indicator.calculate(test_data)
            end_time = time.perf_counter()
            
            execution_time_ms = (end_time - start_time) * 1000
            throughput = data_size / (execution_time_ms / 1000)
            
            results[name] = {
                'execution_time_ms': execution_time_ms,
                'throughput_per_sec': throughput,
                'result_range': [float(np.nanmin(result)), float(np.nanmax(result))],
                'data_size': data_size
            }
        
        return results

# Example usage and testing
if __name__ == "__main__":
    # Initialize backend
    backend = EhlersBackend()
    
    print("Ehlers Backend Integration Test")
    print("=" * 50)
    
    # Test available indicators
    print(f"Available indicators: {backend.get_available_indicators()}")
    print(f"Available transformations: {backend.get_available_transformations()}")
    
    # Benchmark indicators
    print("\nBenchmarking Ehlers indicators...")
    benchmark_results = backend.benchmark_ehlers_indicators(1000)
    
    for name, metrics in benchmark_results.items():
        print(f"{name}: {metrics['execution_time_ms']:.3f}ms ({metrics['throughput_per_sec']:.0f} pts/sec)")
    
    # Test strategy execution
    print("\nTesting strategy execution...")
    strategy_config = {
        'base_indicator': 'super_smoother',
        'transformation': 'stochasticization',
        'signal_threshold': 50.0,
        'lookback_period': 20
    }
    
    symbols = backend.get_available_symbols()[:5]  # Test with first 5 symbols
    results = backend.execute_ehlers_strategy(strategy_config, symbols)
    
    print(f"Processed {results['symbols_processed']} symbols")
    print(f"Generated {results['total_signals']} total signals")
    print(f"Execution time: {results['execution_time']:.3f} seconds")
    
    if results['performance_metrics']:
        print(f"Performance: {results['performance_metrics']['symbols_per_second']:.1f} symbols/sec")
