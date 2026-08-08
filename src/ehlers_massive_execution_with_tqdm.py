#!/usr/bin/env python3
"""
Ehlers Massive Execution with Progress Bars and Strategy-wise Organization
Run all 50 strategies on all 2000+ symbols with detailed monitoring
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
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
warnings.filterwarnings('ignore')

from ehlers_indicators import (
    FisherTransform, InstantaneousTrendline, CGOscillator, RelativeVigorIndex,
    CyberCycleOscillator, Decycler, BandPassFilter, SuperSmoother, RoofingFilter
)
from ehlers_transformations import Stochasticization, Fisherization, CombinedTransformation

class EhlersMassiveExecutionWithTQDM:
    """Execute all 50 Ehlers strategies on all available symbols with progress tracking"""
    
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
            # Check for both formats: symbol=SYMBOL/ and ('SYMBOL',).parquet
            for file_path in data_path.glob("symbol=*/"):
                symbol = file_path.name.replace("symbol=", "")
                symbols.append(symbol)
            
            # Also check for parquet files with tuple format
            for file_path in data_path.glob("('*',).parquet"):
                symbol = file_path.name.replace("('", "").replace("',).parquet", "")
                if symbol not in symbols:
                    symbols.append(symbol)
        
        print(f"Found {len(symbols)} symbols")
        return sorted(symbols)
    
    def load_symbol_data(self, symbol: str) -> Optional[Dict[str, np.ndarray]]:
        """Load OHLCV data for a symbol"""
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
    
    def execute_strategy_on_symbol(self, strategy_id: str, symbol: str) -> Dict[str, Any]:
        """Execute a specific strategy on a specific symbol"""
        if strategy_id not in self.strategies:
            return {'error': f'Strategy {strategy_id} not found'}
        
        strategy_config = self.strategies[strategy_id]
        
        # Load symbol data
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
            
            # Generate signals
            signals = self.generate_signals(indicator_values, signal_type, **signal_params)
            
            # Create detailed trade list with entry date and price
            trade_list = []
            signal_indices = np.where(signals)[0]
            
            for idx in signal_indices:
                if idx < len(data['close']):
                    trade = {
                        'entry_date_index': int(idx),
                        'entry_price': float(data['close'][idx]),
                        'indicator_value': float(indicator_values[idx]) if not np.isnan(indicator_values[idx]) else 0.0,
                        'signal_type': signal_type,
                        'strategy_id': strategy_id,
                        'strategy_name': strategy_config['name'],
                        'symbol': symbol
                    }
                    trade_list.append(trade)
            
            # Calculate metrics
            signal_count = len(signal_indices)
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
        print("Creating strategy folders...")
        
        for strategy_id, strategy_config in self.strategies.items():
            folder_name = f"strategy_{strategy_id}_{strategy_config['name'].replace(' ', '_').replace('/', '_')}"
            folder_path = Path(folder_name)
            folder_path.mkdir(exist_ok=True)
            self.strategy_folders[strategy_id] = folder_path
            print(f"Created folder: {folder_name}")
    
    def execute_all_strategies_on_all_symbols(self) -> Dict[str, Any]:
        """Execute all 50 strategies on all symbols with progress bars"""
        print("Starting massive execution of all strategies on all symbols...")
        
        # Get all symbols
        all_symbols = self.get_all_symbols()
        
        print(f"Executing {len(self.strategies)} strategies on {len(all_symbols)} symbols...")
        print(f"Total executions: {len(self.strategies) * len(all_symbols):,}")
        
        # Create strategy folders
        self.create_strategy_folders()
        
        start_time = time.time()
        total_executions = 0
        successful_executions = 0
        
        # Execute each strategy on each symbol with progress bars
        for strategy_id, strategy_config in tqdm(self.strategies.items(), 
                                                desc="Strategies", 
                                                position=0, 
                                                leave=True):
            
            strategy_results = {}
            strategy_trades = []
            
            # Progress bar for symbols within each strategy
            for symbol in tqdm(all_symbols, 
                             desc=f"Strategy {strategy_id}", 
                             position=1, 
                             leave=False):
                
                result = self.execute_strategy_on_symbol(strategy_id, symbol)
                # Drop heavy trades list from in-memory aggregation to reduce memory footprint
                trades_for_strategy = result.get('trades', None)
                if 'trades' in result:
                    try:
                        del result['trades']
                    except Exception:
                        pass
                strategy_results[symbol] = result
                
                total_executions += 1
                if result.get('success', False):
                    successful_executions += 1
                    # Collect trades for this strategy for on-disk persistence only
                    if trades_for_strategy:
                        strategy_trades.extend(trades_for_strategy)
                # Proactively drop local ref
                trades_for_strategy = None
            
            self.all_results[strategy_id] = strategy_results
            
            # Save strategy-specific results
            self.save_strategy_results(strategy_id, strategy_config, strategy_trades)
            
            # Memory cleanup after each strategy
            try:
                import gc
                # Drop per-strategy large containers
                del strategy_trades
                del strategy_results
                # Encourage pandas/numpy to release memory back to OS
                gc.collect()
            except Exception:
                pass
        
        execution_time = time.time() - start_time
        
        # Calculate aggregated results
        self.aggregated_results = self.calculate_aggregated_results()
        
        print(f"\nExecution completed!")
        print(f"Total executions: {total_executions:,}")
        print(f"Successful executions: {successful_executions:,}")
        print(f"Success rate: {successful_executions/total_executions*100:.1f}%")
        print(f"Total execution time: {execution_time:.1f} seconds")
        print(f"Average time per execution: {execution_time/total_executions*1000:.2f}ms")
        
        return {
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'success_rate': successful_executions/total_executions*100,
            'execution_time': execution_time,
            'avg_time_per_execution': execution_time/total_executions*1000,
            'aggregated_results': self.aggregated_results
        }
    
    def save_strategy_results(self, strategy_id: str, strategy_config: Dict, strategy_trades: List[Dict]):
        """Save results for a specific strategy"""
        folder_path = self.strategy_folders[strategy_id]
        
        # Create DataFrame for trades
        if strategy_trades:
            df_trades = pd.DataFrame(strategy_trades)
            
            # Save as CSV
            csv_path = folder_path / f"{strategy_id}_trades.csv"
            df_trades.to_csv(csv_path, index=False)
            
            # Save as Parquet for better performance
            parquet_path = folder_path / f"{strategy_id}_trades.parquet"
            df_trades.to_parquet(parquet_path, index=False)
            
            # Save strategy metadata
            metadata = {
                'strategy_id': strategy_id,
                'strategy_name': strategy_config['name'],
                'base_indicator': strategy_config['base_indicator'],
                'transformation': strategy_config['transformation'],
                'signal_type': strategy_config['signal_type'],
                'signal_params': strategy_config['signal_params'],
                'indicator_params': strategy_config['indicator_params'],
                'total_trades': len(strategy_trades),
                'unique_symbols': df_trades['symbol'].nunique() if 'symbol' in df_trades.columns else 0,
                'date_range': {
                    'start': int(df_trades['entry_date_index'].min()) if 'entry_date_index' in df_trades.columns else 0,
                    'end': int(df_trades['entry_date_index'].max()) if 'entry_date_index' in df_trades.columns else 0
                }
            }
            
            metadata_path = folder_path / f"{strategy_id}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Ensure DataFrame memory is released
            try:
                del df_trades
                import gc
                gc.collect()
            except Exception:
                pass
    
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
                    'avg_signals_per_symbol': np.mean(strategy_signals),
                    'total_signals': np.sum(strategy_signals),
                    'avg_signal_percentage': np.mean(strategy_percentages),
                    'std_signal_percentage': np.std(strategy_percentages)
                }
        
        # Symbol-level aggregation
        symbol_totals = {}
        for strategy_id, strategy_results in self.all_results.items():
            for symbol, result in strategy_results.items():
                if result.get('success', False):
                    if symbol not in symbol_totals:
                        symbol_totals[symbol] = {
                            'total_signals': 0,
                            'strategies_count': 0,
                            'avg_signal_percentage': 0
                        }
                    symbol_totals[symbol]['total_signals'] += result['total_signals']
                    symbol_totals[symbol]['strategies_count'] += 1
                    symbol_totals[symbol]['avg_signal_percentage'] += result['signal_percentage']
        
        # Calculate averages for symbols
        for symbol in symbol_totals:
            if symbol_totals[symbol]['strategies_count'] > 0:
                symbol_totals[symbol]['avg_signal_percentage'] /= symbol_totals[symbol]['strategies_count']
        
        aggregated['symbol_summary'] = symbol_totals
        
        # Overall metrics
        all_signals = []
        all_percentages = []
        for strategy_summary in aggregated['strategy_summary'].values():
            all_signals.append(strategy_summary['total_signals'])
            all_percentages.append(strategy_summary['avg_signal_percentage'])
        
        if all_signals:  # Only calculate if we have data
            total_signals = np.sum(all_signals)
            total_symbols = len(symbol_totals)
            total_strategies = len(self.strategies)
            
            # Calculate universe-wide metrics
            avg_signals_per_day = total_signals / (total_symbols * 250) if total_symbols > 0 else 0  # Assuming 250 trading days per year
            avg_signals_per_strategy = np.mean(all_signals)
            avg_signals_per_symbol = total_signals / total_symbols if total_symbols > 0 else 0
            
            aggregated['overall_metrics'] = {
                'total_strategies': total_strategies,
                'total_symbols': total_symbols,
                'total_signals_generated': total_signals,
                'avg_signals_per_strategy': avg_signals_per_strategy,
                'avg_signals_per_symbol': avg_signals_per_symbol,
                'avg_signals_per_day': avg_signals_per_day,
                'avg_signal_percentage': np.mean(all_percentages),
                'most_active_strategy': max(aggregated['strategy_summary'].keys(), 
                                          key=lambda x: aggregated['strategy_summary'][x]['total_signals']),
                'most_active_symbol': max(symbol_totals.keys(), 
                                        key=lambda x: symbol_totals[x]['total_signals']),
                'universe_metrics': {
                    'total_trading_opportunities': total_signals,
                    'signals_per_trading_day': avg_signals_per_day,
                    'coverage_ratio': (total_symbols * total_strategies) / (total_symbols * total_strategies) * 100,
                    'signal_density': total_signals / (total_symbols * total_strategies) if total_symbols > 0 else 0
                }
            }
        else:
            aggregated['overall_metrics'] = {
                'total_strategies': len(self.strategies),
                'total_symbols': 0,
                'total_signals_generated': 0,
                'avg_signals_per_strategy': 0,
                'avg_signals_per_symbol': 0,
                'avg_signals_per_day': 0,
                'avg_signal_percentage': 0,
                'most_active_strategy': 'N/A',
                'most_active_symbol': 'N/A'
            }
        
        return aggregated
    
    def export_results(self):
        """Export all results to files"""
        print("Exporting results...")
        
        # Export aggregated results
        with open('ehlers_massive_execution_aggregated.json', 'w') as f:
            json.dump(self.aggregated_results, f, indent=2)
        
        # Export summary report
        self.create_summary_report()
        
        print("Results exported successfully!")
    
    def create_summary_report(self):
        """Create a comprehensive summary report"""
        report = []
        report.append("EHLERS MASSIVE EXECUTION SUMMARY REPORT")
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
        report.append(f"  Average Signals per Day: {overall['avg_signals_per_day']:.1f}")
        report.append(f"  Average Signal Percentage: {overall['avg_signal_percentage']:.2f}%")
        report.append(f"  Most Active Strategy: {overall['most_active_strategy']}")
        report.append(f"  Most Active Symbol: {overall['most_active_symbol']}")
        report.append("")
        
        # Universe metrics
        if 'universe_metrics' in overall:
            universe = overall['universe_metrics']
            report.append("UNIVERSE PERFORMANCE METRICS:")
            report.append(f"  Total Trading Opportunities: {universe['total_trading_opportunities']:,}")
            report.append(f"  Signals per Trading Day: {universe['signals_per_trading_day']:.1f}")
            report.append(f"  Coverage Ratio: {universe['coverage_ratio']:.1f}%")
            report.append(f"  Signal Density: {universe['signal_density']:.3f}")
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
            report.append("")
        
        # Strategy folder information
        report.append("STRATEGY FOLDERS CREATED:")
        for strategy_id, folder_path in self.strategy_folders.items():
            strategy_name = self.strategies[strategy_id]['name']
            report.append(f"  {strategy_id}: {folder_path.name} ({strategy_name})")
        
        # Save report
        with open('ehlers_massive_execution_report.txt', 'w') as f:
            f.write('\n'.join(report))
        
        print("Summary report created: ehlers_massive_execution_report.txt")

def main():
    """Main function to run massive execution"""
    print("EHLERS MASSIVE EXECUTION WITH PROGRESS BARS")
    print("=" * 60)
    
    # Initialize execution engine
    executor = EhlersMassiveExecutionWithTQDM()
    
    # Execute all strategies on all symbols
    results = executor.execute_all_strategies_on_all_symbols()
    
    # Export results
    executor.export_results()
    
    print("\nMassive execution completed successfully!")
    print("Check the following for results:")
    print("  - Individual strategy folders with trade lists")
    print("  - ehlers_massive_execution_aggregated.json")
    print("  - ehlers_massive_execution_report.txt")

if __name__ == "__main__":
    main()
