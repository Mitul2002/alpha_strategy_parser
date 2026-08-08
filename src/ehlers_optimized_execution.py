#!/usr/bin/env python3
"""
Ehlers Optimized Execution - Fixed Performance Bottlenecks
Optimized signal generation and trade creation
"""

import numpy as np
import pandas as pd
import time
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import warnings
from tqdm import tqdm
warnings.filterwarnings('ignore')

from ehlers_indicators import (
    FisherTransform, InstantaneousTrendline, CGOscillator, RelativeVigorIndex,
    CyberCycleOscillator, Decycler, BandPassFilter, SuperSmoother, RoofingFilter
)
from ehlers_transformations import Stochasticization, Fisherization, CombinedTransformation

class EhlersOptimizedExecution:
    """Optimized execution engine with performance improvements"""
    
    def __init__(self, data_path: str = "../../context/rsi_forward_returns/data_partitioned"):
        self.data_path = data_path
        
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
        
        # Results storage
        self.all_results = {}
        self.aggregated_results = {}
        self.strategy_folders = {}
        
        print(f"Initialized with {len(self.strategies)} strategies")
    
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
            }
        }
    
    def get_all_symbols(self) -> List[str]:
        """Get all available symbols from data directory"""
        symbols = []
        data_path = Path(self.data_path)
        
        if data_path.exists():
            symbol_dirs = list(data_path.glob("symbol=*/"))
            parquet_files = list(data_path.glob("('*',).parquet"))
            
            for file_path in symbol_dirs:
                symbol = file_path.name.replace("symbol=", "")
                symbols.append(symbol)
            
            for file_path in parquet_files:
                symbol = file_path.name.replace("('", "").replace("',).parquet", "")
                if symbol not in symbols:
                    symbols.append(symbol)
        
        # Optional cap via env var for smoke runs
        max_symbols = os.environ.get('MAX_SYMBOLS')
        symbols = sorted(symbols)
        if max_symbols:
            try:
                cap = int(max_symbols)
                symbols = symbols[:cap]
            except Exception:
                pass
        
        return symbols
    
    def load_symbol_data(self, symbol: str) -> Optional[Dict[str, np.ndarray]]:
        """Load OHLCV data for a symbol - OPTIMIZED"""
        try:
            data_path = Path(self.data_path)
            
            # Try symbol=SYMBOL/ format first
            symbol_dir = data_path / f"symbol={symbol}"
            parquet_file = symbol_dir / f"symbol={symbol}.parquet"
            
            if not parquet_file.exists():
                # Try tuple format
                parquet_file = data_path / f"('{symbol}',).parquet"
            
            if not parquet_file.exists():
                return None
            
            # Load data using pandas - OPTIMIZED: only load close prices
            df = pd.read_parquet(parquet_file, columns=['close'])
            
            # Convert to numpy array directly
            close_prices = df['close'].values
            
            # Check for valid data
            if len(close_prices) < 50:
                return None
            
            return {'close': close_prices}
            
        except Exception as e:
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
    
    def generate_signals_optimized(self, indicator_values: np.ndarray, signal_type: str = 'threshold', **params) -> np.ndarray:
        """OPTIMIZED signal generation using vectorized operations"""
        if signal_type == 'threshold':
            threshold = params.get('threshold', 0.0)
            return indicator_values > threshold
        
        elif signal_type == 'crossover':
            # Vectorized crossover detection
            signals = np.zeros_like(indicator_values, dtype=bool)
            signals[1:] = indicator_values[1:] > indicator_values[:-1]
            return signals
        
        elif signal_type == 'zero_cross':
            # Vectorized zero crossing
            signals = np.zeros_like(indicator_values, dtype=bool)
            signals[1:] = (indicator_values[1:] > 0) & (indicator_values[:-1] <= 0)
            return signals
        
        elif signal_type == 'extreme':
            # Vectorized extreme detection
            percentile = params.get('percentile', 90)
            upper_threshold = np.nanpercentile(indicator_values, percentile)
            lower_threshold = np.nanpercentile(indicator_values, 100 - percentile)
            return (indicator_values > upper_threshold) | (indicator_values < lower_threshold)
        
        return np.zeros_like(indicator_values, dtype=bool)
    
    def create_trades_optimized(self, signals: np.ndarray, prices: np.ndarray, 
                              indicator_values: np.ndarray, strategy_id: str, 
                              strategy_name: str, symbol: str) -> List[Dict]:
        """OPTIMIZED trade creation using vectorized operations"""
        # Find signal indices in one operation
        signal_indices = np.where(signals)[0]
        
        if len(signal_indices) == 0:
            return []
        
        # Create trades using vectorized operations
        trades = []
        for idx in signal_indices:
            if idx < len(prices):
                trades.append({
                    'entry_date_index': int(idx),
                    'entry_price': float(prices[idx]),
                    'indicator_value': float(indicator_values[idx]) if not np.isnan(indicator_values[idx]) else 0.0,
                    'signal_type': 'threshold',  # Default
                    'strategy_id': strategy_id,
                    'strategy_name': strategy_name,
                    'symbol': symbol
                })
        
        return trades
    
    def execute_strategy_on_symbol_optimized(self, strategy_id: str, symbol: str) -> Dict[str, Any]:
        """OPTIMIZED strategy execution on a symbol"""
        if strategy_id not in self.strategies:
            return {'error': f'Strategy {strategy_id} not found'}
        
        strategy_config = self.strategies[strategy_id]
        
        # Load symbol data (only close prices)
        data = self.load_symbol_data(symbol)
        if data is None:
            return {'error': f'No data for {symbol}'}
        
        try:
            # Extract strategy configuration
            base_indicator = strategy_config['base_indicator']
            transformation = strategy_config['transformation']
            signal_type = strategy_config['signal_type']
            signal_params = strategy_config['signal_params']
            indicator_params = strategy_config['indicator_params']
            
            # Calculate enhanced indicator
            indicator_values = self.get_enhanced_indicator(
                base_indicator, transformation, data['close'], **indicator_params
            )
            
            # Generate signals (OPTIMIZED)
            signals = self.generate_signals_optimized(indicator_values, signal_type, **signal_params)
            
            # Create trades (OPTIMIZED)
            trade_list = self.create_trades_optimized(
                signals, data['close'], indicator_values, 
                strategy_id, strategy_config['name'], symbol
            )
            
            # Calculate metrics
            signal_count = len(trade_list)
            total_days = len(data['close'])
            signal_percentage = (signal_count / total_days * 100) if total_days > 0 else 0
            
            result = {
                'symbol': symbol,
                'strategy_id': strategy_id,
                'strategy_name': strategy_config['name'],
                'total_signals': signal_count,
                'total_days': total_days,
                'signal_percentage': signal_percentage,
                'avg_indicator_value': float(np.nanmean(indicator_values)),
                'indicator_std': float(np.nanstd(indicator_values)),
                'trades': trade_list,
                'success': True
            }
            
            return result
            
        except Exception as e:
            return {
                'symbol': symbol,
                'strategy_id': strategy_id,
                'error': str(e),
                'success': False
            }
    
    def create_strategy_folders(self):
        """Create folders for each strategy"""
        for strategy_id, strategy_config in self.strategies.items():
            folder_name = f"strategy_{strategy_id}_{strategy_config['name'].replace(' ', '_').replace('/', '_')}"
            folder_path = Path(folder_name)
            folder_path.mkdir(exist_ok=True)
            self.strategy_folders[strategy_id] = folder_path
    
    def execute_all_strategies_on_all_symbols_optimized(self) -> Dict[str, Any]:
        """OPTIMIZED execution of all strategies on all symbols"""
        print("Starting OPTIMIZED massive execution...")
        
        # Get all symbols
        all_symbols = self.get_all_symbols()
        
        if len(all_symbols) == 0:
            print("No symbols found! Check data path.")
            return {'error': 'No symbols found'}
        
        print(f"Executing {len(self.strategies)} strategies on {len(all_symbols)} symbols...")
        print(f"Total executions: {len(self.strategies) * len(all_symbols):,}")
        
        # Create per-strategy folders
        self.create_strategy_folders()
        
        start_time = time.time()
        total_executions = 0
        successful_executions = 0
        
        # OPTIMIZED: Process strategies in batches to reduce memory usage
        batch_size = 10  # Process 10 strategies at a time
        
        for batch_start in range(0, len(self.strategies), batch_size):
            batch_end = min(batch_start + batch_size, len(self.strategies))
            batch_strategies = list(self.strategies.items())[batch_start:batch_end]
            
            print(f"Processing batch {batch_start//batch_size + 1}/{(len(self.strategies) + batch_size - 1)//batch_size}")
            
            # Execute batch of strategies
            for strategy_id, strategy_config in tqdm(batch_strategies, 
                                                    desc=f"Batch {batch_start//batch_size + 1}", 
                                                    position=0, 
                                                    leave=True):
                
                strategy_results = {}
                strategy_trades = []
                
                # Process symbols for this strategy
                for symbol in tqdm(all_symbols, 
                                 desc=f"Strategy {strategy_id}", 
                                 position=1, 
                                 leave=False):
                    
                    result = self.execute_strategy_on_symbol_optimized(strategy_id, symbol)
                    strategy_results[symbol] = result
                    
                    total_executions += 1
                    if result.get('success', False):
                        successful_executions += 1
                        strategy_trades.extend(result.get('trades', []))
                
                self.all_results[strategy_id] = strategy_results
                
                # Save strategy results immediately to free memory
                self.save_strategy_results_optimized(strategy_id, strategy_config, strategy_trades)
        
        execution_time = time.time() - start_time
        
        # Calculate aggregated results
        self.aggregated_results = self.calculate_aggregated_results()
        
        print(f"\nOPTIMIZED Execution completed!")
        print(f"Total executions: {total_executions:,}")
        print(f"Successful executions: {successful_executions:,}")
        print(f"Success rate: {successful_executions/total_executions*100:.1f}%")
        print(f"Total execution time: {execution_time:.1f} seconds")
        print(f"Average time per execution: {execution_time/total_executions*1000:.2f}ms")
        
        # Generate RELIANCE trade list if present
        try:
            self.generate_reliance_trade_list()
        except Exception:
            pass
        
        return {
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'success_rate': successful_executions/total_executions*100,
            'execution_time': execution_time,
            'avg_time_per_execution': execution_time/total_executions*1000,
            'aggregated_results': self.aggregated_results
        }
    
    def save_strategy_results_optimized(self, strategy_id: str, strategy_config: Dict, strategy_trades: List[Dict]):
        """OPTIMIZED strategy results saving"""
        folder_path = self.strategy_folders.get(strategy_id, Path('.'))
        
        if not strategy_trades:
            # still write empty metadata for traceability
            metadata = {
                'strategy_id': strategy_id,
                'strategy_name': strategy_config['name'],
                'total_trades': 0,
                'unique_symbols': 0
            }
            metadata_path = folder_path / f"{strategy_id}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            return
        
        # Create DataFrame efficiently
        df_trades = pd.DataFrame(strategy_trades)
        
        # Save as CSV and Parquet inside the strategy folder
        csv_path = folder_path / f"{strategy_id}_trades.csv"
        df_trades.to_csv(csv_path, index=False)
        
        parquet_path = folder_path / f"{strategy_id}_trades.parquet"
        df_trades.to_parquet(parquet_path, index=False)
        
        # Save metadata
        metadata = {
            'strategy_id': strategy_id,
            'strategy_name': strategy_config['name'],
            'base_indicator': strategy_config['base_indicator'],
            'transformation': strategy_config['transformation'],
            'signal_type': strategy_config['signal_type'],
            'signal_params': strategy_config['signal_params'],
            'indicator_params': strategy_config['indicator_params'],
            'total_trades': int(len(strategy_trades)),
            'unique_symbols': int(df_trades['symbol'].nunique() if 'symbol' in df_trades.columns else 0)
        }
        
        metadata_path = folder_path / f"{strategy_id}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def generate_reliance_trade_list(self):
        """Generate a consolidated RELIANCE trade list across all strategies"""
        target_symbol = 'RELIANCE'
        trades = []
        for strategy_id, results_by_symbol in self.all_results.items():
            res = results_by_symbol.get(target_symbol)
            if res and res.get('success') and res.get('trades'):
                for t in res['trades']:
                    trades.append({
                        'strategy_id': strategy_id,
                        'strategy_name': res.get('strategy_name'),
                        'entry_date_index': t['entry_date_index'],
                        'entry_price': t['entry_price'],
                        'indicator_value': t.get('indicator_value', np.nan)
                    })
        if trades:
            df = pd.DataFrame(trades)
            df.to_csv('RELIANCE_trades_all_strategies.csv', index=False)
            df.to_parquet('RELIANCE_trades_all_strategies.parquet', index=False)
    
    def calculate_aggregated_results(self) -> Dict[str, Any]:
        """Calculate aggregated results across all strategies and symbols"""
        print("Calculating aggregated results...")
        
        aggregated = {
            'strategy_summary': {},
            'symbol_summary': {},
            'overall_metrics': {}
        }
        
        # Strategy-level aggregation
        for strategy_id, strategy_results in self.all_results.items():
            strategy_signals = []
            strategy_percentages = []
            successful_symbols = 0
            
            for symbol, result in strategy_results.items():
                if result.get('success', False):
                    strategy_signals.append(result['total_signals'])
                    strategy_percentages.append(result['signal_percentage'])
                    successful_symbols += 1
            
            if strategy_signals:
                aggregated['strategy_summary'][strategy_id] = {
                    'strategy_name': self.strategies[strategy_id]['name'],
                    'successful_symbols': successful_symbols,
                    'total_symbols': len(strategy_results),
                    'success_rate': successful_symbols / len(strategy_results) * 100,
                    'avg_signals_per_symbol': float(np.mean(strategy_signals)),
                    'total_signals': int(np.sum(strategy_signals)),
                    'avg_signal_percentage': float(np.mean(strategy_percentages))
                }
        
        # Symbol-level aggregation
        symbol_totals = {}
        for strategy_id, strategy_results in self.all_results.items():
            for symbol, result in strategy_results.items():
                if result.get('success', False):
                    if symbol not in symbol_totals:
                        symbol_totals[symbol] = {
                            'total_signals': 0,
                            'strategies_count': 0
                        }
                    symbol_totals[symbol]['total_signals'] += result['total_signals']
                    symbol_totals[symbol]['strategies_count'] += 1
        
        aggregated['symbol_summary'] = symbol_totals
        
        # Overall metrics
        all_signals = []
        all_percentages = []
        for strategy_summary in aggregated['strategy_summary'].values():
            all_signals.append(strategy_summary['total_signals'])
            all_percentages.append(strategy_summary['avg_signal_percentage'])
        
        if all_signals:
            total_signals = int(np.sum(all_signals))
            total_symbols = int(len(symbol_totals))
            total_strategies = int(len(self.strategies))
            
            aggregated['overall_metrics'] = {
                'total_strategies': total_strategies,
                'total_symbols': total_symbols,
                'total_signals_generated': total_signals,
                'avg_signals_per_strategy': float(np.mean(all_signals)),
                'avg_signals_per_symbol': float(total_signals / total_symbols) if total_symbols > 0 else 0.0,
                'avg_signal_percentage': float(np.mean(all_percentages)) if all_percentages else 0.0,
                'most_active_strategy': max(aggregated['strategy_summary'].keys(), 
                                          key=lambda x: aggregated['strategy_summary'][x]['total_signals']) if aggregated['strategy_summary'] else 'N/A',
                'most_active_symbol': max(symbol_totals.keys(), 
                                        key=lambda x: symbol_totals[x]['total_signals']) if symbol_totals else 'N/A'
            }
        
        return aggregated
    
    def export_results(self):
        """Export all results to files"""
        print("Exporting results...")
        
        # Export aggregated results
        with open('ehlers_optimized_execution_aggregated.json', 'w') as f:
            json.dump(self.aggregated_results, f, indent=2)
        
        # Export summary report
        self.create_summary_report()
        
        print("Results exported successfully!")
    
    def create_summary_report(self):
        """Create a comprehensive summary report"""
        report = []
        report.append("EHLERS OPTIMIZED EXECUTION SUMMARY REPORT")
        report.append("=" * 60)
        report.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall metrics
        overall = self.aggregated_results['overall_metrics']
        report.append("UNIVERSE-WIDE METRICS:")
        report.append(f"  Total Strategies: {overall['total_strategies']}")
        report.append(f"  Total Symbols: {overall['total_symbols']}")
        report.append(f"  Total Signals Generated: {overall['total_signals_generated']:,}")
        report.append(f"  Average Signals per Strategy: {overall['avg_signals_per_strategy']:.1f}")
        report.append(f"  Average Signals per Symbol: {overall['avg_signals_per_symbol']:.1f}")
        report.append(f"  Average Signal Percentage: {overall['avg_signal_percentage']:.2f}%")
        report.append(f"  Most Active Strategy: {overall['most_active_strategy']}")
        report.append(f"  Most Active Symbol: {overall['most_active_symbol']}")
        report.append("")
        
        # Top 10 strategies by signal count
        if self.aggregated_results['strategy_summary']:
            report.append("TOP 10 STRATEGIES BY SIGNAL COUNT:")
            strategy_signals = [(k, v['total_signals']) for k, v in self.aggregated_results['strategy_summary'].items()]
            strategy_signals.sort(key=lambda x: x[1], reverse=True)
            
            for i, (strategy_id, signal_count) in enumerate(strategy_signals[:10]):
                strategy_name = self.aggregated_results['strategy_summary'][strategy_id]['strategy_name']
                report.append(f"  {i+1:2d}. {strategy_id}: {signal_count:,} signals ({strategy_name})")
            report.append("")
        
        # Top 10 symbols by signal count
        if self.aggregated_results['symbol_summary']:
            report.append("TOP 10 SYMBOLS BY SIGNAL COUNT:")
            symbol_signals = [(k, v['total_signals']) for k, v in self.aggregated_results['symbol_summary'].items()]
            symbol_signals.sort(key=lambda x: x[1], reverse=True)
            
            for i, (symbol, signal_count) in enumerate(symbol_signals[:10]):
                report.append(f"  {i+1:2d}. {symbol}: {signal_count:,} signals")
        
        # Strategy folder information
        report.append("")
        report.append("STRATEGY FOLDERS CREATED:")
        for strategy_id, folder_path in self.strategy_folders.items():
            strategy_name = self.strategies[strategy_id]['name']
            report.append(f"  {strategy_id}: {folder_path.name} ({strategy_name})")
        
        # Save report
        with open('ehlers_optimized_execution_report.txt', 'w') as f:
            f.write('\n'.join(report))
        
        print("Summary report created: ehlers_optimized_execution_report.txt")

def main():
    """Main function to run optimized execution"""
    print("EHLERS OPTIMIZED EXECUTION")
    print("=" * 60)
    
    # Initialize execution engine
    executor = EhlersOptimizedExecution()
    
    # Execute all strategies on all symbols
    results = executor.execute_all_strategies_on_all_symbols_optimized()
    
    # Export results
    executor.export_results()
    
    print("\nOptimized execution completed successfully!")
    print("Check the following for results:")
    print("  - Individual strategy parquet files")
    print("  - ehlers_optimized_execution_aggregated.json")
    print("  - ehlers_optimized_execution_report.txt")

if __name__ == "__main__":
    main()
