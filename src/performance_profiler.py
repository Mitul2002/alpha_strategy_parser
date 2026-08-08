#!/usr/bin/env python3
"""
Performance Profiler for Ehlers Execution
Identify bottlenecks in the massive execution
"""

import time
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class PerformanceProfiler:
    """Profile the performance bottlenecks in Ehlers execution"""
    
    def __init__(self, data_path: str = "../../context/rsi_forward_returns/data_partitioned"):
        self.data_path = data_path
        self.profile_results = {}
        
    def get_sample_symbols(self, count: int = 10) -> List[str]:
        """Get a sample of symbols for testing"""
        symbols = []
        data_path = Path(self.data_path)
        
        if data_path.exists():
            symbol_dirs = list(data_path.glob("symbol=*/"))
            for file_path in symbol_dirs[:count]:
                symbol = file_path.name.replace("symbol=", "")
                symbols.append(symbol)
        
        return symbols
    
    def profile_data_loading(self, symbols: List[str]) -> Dict[str, float]:
        """Profile data loading performance"""
        print("Profiling data loading...")
        results = {}
        
        for symbol in symbols:
            start_time = time.time()
            
            try:
                data_path = Path(self.data_path)
                symbol_dir = data_path / f"symbol={symbol}"
                parquet_file = symbol_dir / f"symbol={symbol}.parquet"
                
                if not parquet_file.exists():
                    parquet_file = data_path / f"('{symbol}',).parquet"
                
                if parquet_file.exists():
                    df = pd.read_parquet(parquet_file)
                    load_time = time.time() - start_time
                    results[symbol] = {
                        'load_time': load_time,
                        'data_size': len(df),
                        'columns': list(df.columns)
                    }
                    print(f"  {symbol}: {load_time:.3f}s ({len(df)} rows)")
                else:
                    results[symbol] = {'load_time': 0, 'data_size': 0, 'error': 'File not found'}
                    
            except Exception as e:
                results[symbol] = {'load_time': 0, 'data_size': 0, 'error': str(e)}
                print(f"  {symbol}: ERROR - {e}")
        
        return results
    
    def profile_indicator_calculation(self, data_size: int = 1000) -> Dict[str, float]:
        """Profile indicator calculation performance"""
        print("Profiling indicator calculations...")
        
        # Create sample data
        np.random.seed(42)
        sample_data = np.random.randn(data_size).cumsum() + 100
        
        results = {}
        
        # Test each indicator
        from ehlers_indicators import (
            FisherTransform, InstantaneousTrendline, CGOscillator, RelativeVigorIndex,
            CyberCycleOscillator, Decycler, BandPassFilter, SuperSmoother, RoofingFilter
        )
        
        indicators = {
            'FisherTransform': FisherTransform(10),
            'InstantaneousTrendline': InstantaneousTrendline(0.07),
            'CGOscillator': CGOscillator(10),
            'RelativeVigorIndex': RelativeVigorIndex(10),
            'CyberCycleOscillator': CyberCycleOscillator(10),
            'Decycler': Decycler(40),
            'BandPassFilter': BandPassFilter(10, 20),
            'SuperSmoother': SuperSmoother(10),
            'RoofingFilter': RoofingFilter(40)
        }
        
        for name, indicator in indicators.items():
            start_time = time.time()
            try:
                result = indicator.calculate(sample_data)
                calc_time = time.time() - start_time
                results[name] = {
                    'calc_time': calc_time,
                    'data_size': data_size,
                    'throughput': data_size / calc_time if calc_time > 0 else 0
                }
                print(f"  {name}: {calc_time:.3f}s ({data_size/calc_time:.0f} pts/sec)")
            except Exception as e:
                results[name] = {'calc_time': 0, 'error': str(e)}
                print(f"  {name}: ERROR - {e}")
        
        return results
    
    def profile_file_operations(self, symbols: List[str]) -> Dict[str, float]:
        """Profile file I/O operations"""
        print("Profiling file operations...")
        results = {}
        
        # Test CSV writing
        start_time = time.time()
        test_data = pd.DataFrame({
            'symbol': symbols * 10,
            'value': np.random.randn(len(symbols) * 10),
            'date': range(len(symbols) * 10)
        })
        
        csv_time = time.time() - start_time
        results['csv_creation'] = csv_time
        
        # Test CSV writing to file
        start_time = time.time()
        test_data.to_csv('test_output.csv', index=False)
        csv_write_time = time.time() - start_time
        results['csv_write'] = csv_write_time
        
        # Test Parquet writing
        start_time = time.time()
        test_data.to_parquet('test_output.parquet', index=False)
        parquet_write_time = time.time() - start_time
        results['parquet_write'] = parquet_write_time
        
        print(f"  CSV creation: {csv_time:.3f}s")
        print(f"  CSV write: {csv_write_time:.3f}s")
        print(f"  Parquet write: {parquet_write_time:.3f}s")
        
        # Cleanup
        Path('test_output.csv').unlink(missing_ok=True)
        Path('test_output.parquet').unlink(missing_ok=True)
        
        return results
    
    def profile_full_execution(self, symbols: List[str], strategies_count: int = 5) -> Dict[str, float]:
        """Profile a full execution cycle"""
        print("Profiling full execution cycle...")
        
        from ehlers_indicators import FisherTransform, InstantaneousTrendline
        
        results = {}
        
        # Load data for all symbols
        start_time = time.time()
        symbol_data = {}
        for symbol in symbols:
            try:
                data_path = Path(self.data_path)
                symbol_dir = data_path / f"symbol={symbol}"
                parquet_file = symbol_dir / f"symbol={symbol}.parquet"
                
                if not parquet_file.exists():
                    parquet_file = data_path / f"('{symbol}',).parquet"
                
                if parquet_file.exists():
                    df = pd.read_parquet(parquet_file)
                    symbol_data[symbol] = df['close'].values
            except:
                continue
        
        data_load_time = time.time() - start_time
        results['data_load_time'] = data_load_time
        print(f"  Data loading for {len(symbols)} symbols: {data_load_time:.3f}s")
        
        # Calculate indicators for all symbols
        start_time = time.time()
        indicator = FisherTransform(10)
        for symbol, data in symbol_data.items():
            if len(data) > 50:
                indicator.calculate(data)
        
        indicator_calc_time = time.time() - start_time
        results['indicator_calc_time'] = indicator_calc_time
        print(f"  Indicator calculation for {len(symbol_data)} symbols: {indicator_calc_time:.3f}s")
        
        # Generate signals
        start_time = time.time()
        total_signals = 0
        for symbol, data in symbol_data.items():
            if len(data) > 50:
                indicator_values = indicator.calculate(data)
                signals = indicator_values > 0
                total_signals += np.sum(signals)
        
        signal_gen_time = time.time() - start_time
        results['signal_gen_time'] = signal_gen_time
        results['total_signals'] = total_signals
        print(f"  Signal generation: {signal_gen_time:.3f}s ({total_signals} signals)")
        
        # File operations
        start_time = time.time()
        trade_data = []
        for symbol, data in symbol_data.items():
            if len(data) > 50:
                indicator_values = indicator.calculate(data)
                signals = indicator_values > 0
                signal_indices = np.where(signals)[0]
                
                for idx in signal_indices:
                    trade_data.append({
                        'symbol': symbol,
                        'entry_date_index': int(idx),
                        'entry_price': float(data[idx]),
                        'indicator_value': float(indicator_values[idx])
                    })
        
        trade_creation_time = time.time() - start_time
        results['trade_creation_time'] = trade_creation_time
        print(f"  Trade creation: {trade_creation_time:.3f}s ({len(trade_data)} trades)")
        
        return results
    
    def run_full_profile(self):
        """Run complete performance profiling"""
        print("EHLERS EXECUTION PERFORMANCE PROFILER")
        print("=" * 50)
        
        # Get sample symbols
        symbols = self.get_sample_symbols(20)
        print(f"Testing with {len(symbols)} symbols: {symbols[:5]}...")
        print()
        
        # Profile each component
        self.profile_results['data_loading'] = self.profile_data_loading(symbols[:10])
        print()
        
        self.profile_results['indicator_calculation'] = self.profile_indicator_calculation(1000)
        print()
        
        self.profile_results['file_operations'] = self.profile_file_operations(symbols[:5])
        print()
        
        self.profile_results['full_execution'] = self.profile_full_execution(symbols[:10], 5)
        print()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print performance summary"""
        print("PERFORMANCE SUMMARY")
        print("=" * 30)
        
        # Data loading summary
        data_loading = self.profile_results['data_loading']
        successful_loads = [v for v in data_loading.values() if 'error' not in v]
        if successful_loads:
            avg_load_time = np.mean([v['load_time'] for v in successful_loads])
            avg_data_size = np.mean([v['data_size'] for v in successful_loads])
            print(f"Data Loading:")
            print(f"  Average load time: {avg_load_time:.3f}s per symbol")
            print(f"  Average data size: {avg_data_size:.0f} rows")
            print(f"  Estimated time for 2000 symbols: {avg_load_time * 2000:.1f}s")
        
        # Indicator calculation summary
        indicator_calc = self.profile_results['indicator_calculation']
        successful_calcs = [v for v in indicator_calc.values() if 'error' not in v]
        if successful_calcs:
            avg_calc_time = np.mean([v['calc_time'] for v in successful_calcs])
            avg_throughput = np.mean([v['throughput'] for v in successful_calcs])
            print(f"Indicator Calculation:")
            print(f"  Average calculation time: {avg_calc_time:.3f}s per indicator")
            print(f"  Average throughput: {avg_throughput:.0f} points/sec")
            print(f"  Estimated time for 50 strategies × 2000 symbols: {avg_calc_time * 50 * 2000:.1f}s")
        
        # Full execution summary
        full_exec = self.profile_results['full_execution']
        if full_exec:
            total_time = (full_exec.get('data_load_time', 0) + 
                         full_exec.get('indicator_calc_time', 0) + 
                         full_exec.get('signal_gen_time', 0) + 
                         full_exec.get('trade_creation_time', 0))
            
            print(f"Full Execution (10 symbols, 1 strategy):")
            print(f"  Total time: {total_time:.3f}s")
            print(f"  Data loading: {full_exec.get('data_load_time', 0):.3f}s")
            print(f"  Indicator calc: {full_exec.get('indicator_calc_time', 0):.3f}s")
            print(f"  Signal generation: {full_exec.get('signal_gen_time', 0):.3f}s")
            print(f"  Trade creation: {full_exec.get('trade_creation_time', 0):.3f}s")
            print(f"  Estimated time for 50 strategies × 2000 symbols: {total_time * 50 * 200:.1f}s")

def main():
    profiler = PerformanceProfiler()
    profiler.run_full_profile()

if __name__ == "__main__":
    main()
