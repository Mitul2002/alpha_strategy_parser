#!/usr/bin/env python3
"""
Quick test of Ehlers strategies on a subset of symbols including RELIANCE
"""

import numpy as np
import pandas as pd
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

from ehlers_indicators import (
    FisherTransform, InstantaneousTrendline, CGOscillator, RelativeVigorIndex,
    CyberCycleOscillator, Decycler, BandPassFilter, SuperSmoother, RoofingFilter
)
from ehlers_transformations import Stochasticization, Fisherization, CombinedTransformation

def load_symbol_data(symbol: str, data_path: str = "../../context/rsi_forward_returns/data_partitioned") -> Optional[Dict[str, np.ndarray]]:
    """Load OHLCV data for a symbol"""
    try:
        data_path = Path(data_path)
        
        # Try symbol=SYMBOL/ format first
        symbol_dir = data_path / f"symbol={symbol}"
        parquet_file = symbol_dir / f"symbol={symbol}.parquet"
        
        if not parquet_file.exists():
            # Try tuple format
            parquet_file = data_path / f"('{symbol}',).parquet"
        
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
            'volume': df['volume'].values if 'volume' in df.columns else None,
            'date': df.index.values if hasattr(df.index, 'values') else None
        }
        
        return data
        
    except Exception as e:
        print(f"Error loading data for {symbol}: {e}")
        return None

def test_ehlers_on_reliance():
    """Test Ehlers indicators on RELIANCE data"""
    print("Testing Ehlers indicators on RELIANCE...")
    
    # Load RELIANCE data
    data = load_symbol_data('RELIANCE')
    if data is None:
        print("Could not load RELIANCE data")
        return
    
    print(f"Loaded RELIANCE data: {len(data['close'])} days")
    print(f"Price range: {data['close'].min():.2f} - {data['close'].max():.2f}")
    
    # Initialize indicators
    indicators = {
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
    
    # Test each indicator
    results = {}
    for name, indicator in indicators.items():
        start_time = time.perf_counter()
        values = indicator.calculate(data['close'])
        end_time = time.perf_counter()
        
        # Generate signals (simple threshold)
        signals = values > 0
        signal_count = np.sum(signals)
        
        results[name] = {
            'execution_time_ms': (end_time - start_time) * 1000,
            'total_signals': int(signal_count),
            'signal_percentage': float(signal_count / len(signals) * 100),
            'avg_value': float(np.nanmean(values)),
            'std_value': float(np.nanstd(values)),
            'min_value': float(np.nanmin(values)),
            'max_value': float(np.nanmax(values))
        }
        
        print(f"{name:25s}: {signal_count:4d} signals ({signal_count/len(signals)*100:5.1f}%) - {results[name]['execution_time_ms']:6.2f}ms")
    
    return results

def test_transformations_on_reliance():
    """Test transformations on RELIANCE data"""
    print("\nTesting transformations on RELIANCE...")
    
    # Load RELIANCE data
    data = load_symbol_data('RELIANCE')
    if data is None:
        print("Could not load RELIANCE data")
        return
    
    # Use Fisher Transform as base
    fisher = FisherTransform(10)
    base_values = fisher.calculate(data['close'])
    
    # Initialize transformations
    transformations = {
        'stochasticization': Stochasticization(10),
        'fisherization': Fisherization(10),
        'combined_transformation': CombinedTransformation(10)
    }
    
    # Test each transformation
    results = {}
    for name, transformation in transformations.items():
        start_time = time.perf_counter()
        transformed_values = transformation.apply(base_values)
        end_time = time.perf_counter()
        
        # Generate signals (simple threshold)
        signals = transformed_values > 0
        signal_count = np.sum(signals)
        
        results[name] = {
            'execution_time_ms': (end_time - start_time) * 1000,
            'total_signals': int(signal_count),
            'signal_percentage': float(signal_count / len(signals) * 100),
            'avg_value': float(np.nanmean(transformed_values)),
            'std_value': float(np.nanstd(transformed_values)),
            'min_value': float(np.nanmin(transformed_values)),
            'max_value': float(np.nanmax(transformed_values))
        }
        
        print(f"{name:25s}: {signal_count:4d} signals ({signal_count/len(signals)*100:5.1f}%) - {results[name]['execution_time_ms']:6.2f}ms")
    
    return results

def test_sample_strategies():
    """Test a few sample strategies on RELIANCE"""
    print("\nTesting sample strategies on RELIANCE...")
    
    # Load RELIANCE data
    data = load_symbol_data('RELIANCE')
    if data is None:
        print("Could not load RELIANCE data")
        return
    
    # Sample strategies
    strategies = {
        'strategy_01': {
            'name': 'Fisher Transform Base',
            'base_indicator': 'fisher_transform',
            'transformation': 'none',
            'signal_type': 'threshold',
            'signal_params': {'threshold': 0.0}
        },
        'strategy_10': {
            'name': 'Fisher Transform Stochastic',
            'base_indicator': 'fisher_transform',
            'transformation': 'stochasticization',
            'signal_type': 'threshold',
            'signal_params': {'threshold': 50.0}
        },
        'strategy_19': {
            'name': 'Fisher Transform Fisher',
            'base_indicator': 'fisher_transform',
            'transformation': 'fisherization',
            'signal_type': 'threshold',
            'signal_params': {'threshold': 0.0}
        }
    }
    
    # Initialize components
    indicators = {
        'fisher_transform': FisherTransform(10),
    }
    
    transformations = {
        'stochasticization': Stochasticization(10),
        'fisherization': Fisherization(10),
    }
    
    results = {}
    for strategy_id, config in strategies.items():
        print(f"\nTesting {strategy_id}: {config['name']}")
        
        # Calculate base indicator
        base_values = indicators[config['base_indicator']].calculate(data['close'])
        
        # Apply transformation
        if config['transformation'] == 'none':
            final_values = base_values
        else:
            final_values = transformations[config['transformation']].apply(base_values)
        
        # Generate signals
        threshold = config['signal_params']['threshold']
        signals = final_values > threshold
        signal_count = np.sum(signals)
        
        # Create trade list
        trade_list = []
        signal_indices = np.where(signals)[0]
        
        for idx in signal_indices[:10]:  # Show first 10 trades
            if idx < len(data['close']):
                trade = {
                    'date_index': int(idx),
                    'price': float(data['close'][idx]),
                    'indicator_value': float(final_values[idx]) if not np.isnan(final_values[idx]) else 0.0,
                    'signal_type': config['signal_type']
                }
                trade_list.append(trade)
        
        results[strategy_id] = {
            'strategy_name': config['name'],
            'total_signals': int(signal_count),
            'signal_percentage': float(signal_count / len(signals) * 100),
            'avg_indicator_value': float(np.nanmean(final_values)),
            'sample_trades': trade_list
        }
        
        print(f"  Total signals: {signal_count}")
        print(f"  Signal percentage: {signal_count/len(signals)*100:.1f}%")
        print(f"  Sample trades (first 10):")
        for trade in trade_list:
            print(f"    Day {trade['date_index']:4d}: Price {trade['price']:8.2f}, Indicator {trade['indicator_value']:8.3f}")
    
    return results

def main():
    """Main function"""
    print("EHLERS QUICK TEST ON RELIANCE")
    print("=" * 50)
    
    # Test indicators
    indicator_results = test_ehlers_on_reliance()
    
    # Test transformations
    transformation_results = test_transformations_on_reliance()
    
    # Test sample strategies
    strategy_results = test_sample_strategies()
    
    # Save results
    all_results = {
        'indicators': indicator_results,
        'transformations': transformation_results,
        'strategies': strategy_results,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('ehlers_quick_test_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nQuick test completed! Results saved to ehlers_quick_test_results.json")
    
    # Summary
    total_indicator_signals = sum(r['total_signals'] for r in indicator_results.values())
    total_transformation_signals = sum(r['total_signals'] for r in transformation_results.values())
    total_strategy_signals = sum(r['total_signals'] for r in strategy_results.values())
    
    print(f"\nSUMMARY:")
    print(f"  Indicator signals: {total_indicator_signals}")
    print(f"  Transformation signals: {total_transformation_signals}")
    print(f"  Strategy signals: {total_strategy_signals}")

if __name__ == "__main__":
    main()
