#!/usr/bin/env python3
"""
Ehlers Massive Execution - Run all 50 strategies on all 2000+ symbols
Generate aggregated results and detailed trade lists
"""

import numpy as np
import pandas as pd
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

from ehlers_indicators import (
    FisherTransform, InstantaneousTrendline, CGOscillator, RelativeVigorIndex,
    CyberCycleOscillator, Decycler, BandPassFilter, SuperSmoother, RoofingFilter
)
from ehlers_transformations import Stochasticization, Fisherization, CombinedTransformation

class EhlersMassiveExecution:
    """Execute all 50 Ehlers strategies on all available symbols"""
    
    def __init__(self, data_path: str = "../context/rsi_forward_returns/data_partitioned"):
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
        self.reliance_trades = {}
        
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
            for file_path in data_path.glob("symbol=*/"):
                symbol = file_path.name.replace("symbol=", "")
                symbols.append(symbol)
        
        print(f"Found {len(symbols)} symbols")
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
                'volume': df['volume'].values if 'volume' in df.columns else None,
                'date': df.index.values if hasattr(df.index, 'values') else None
            }
            
            return data
            
        except Exception as e:
            print(f"Error loading data for {symbol}: {e}")
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
            
            # Create detailed trade list
            trade_list = []
            signal_indices = np.where(signals)[0]
            
            for idx in signal_indices:
                if idx < len(data['close']):
                    trade = {
                        'date_index': int(idx),
                        'price': float(data['close'][idx]),
                        'indicator_value': float(indicator_values[idx]) if not np.isnan(indicator_values[idx]) else 0.0,
                        'signal_type': signal_type,
                        'strategy_id': strategy_id,
                        'strategy_name': strategy_config['name']
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
    
    def execute_all_strategies_on_all_symbols(self, max_symbols: int = None) -> Dict[str, Any]:
        """Execute all 50 strategies on all symbols"""
        print("Starting massive execution of all strategies on all symbols...")
        
        # Get all symbols
        all_symbols = self.get_all_symbols()
        if max_symbols:
            all_symbols = all_symbols[:max_symbols]
        
        print(f"Executing {len(self.strategies)} strategies on {len(all_symbols)} symbols...")
        print(f"Total executions: {len(self.strategies) * len(all_symbols):,}")
        
        start_time = time.time()
        total_executions = 0
        successful_executions = 0
        
        # Execute each strategy on each symbol
        for strategy_id, strategy_config in self.strategies.items():
            print(f"\nExecuting {strategy_id}: {strategy_config['name']}")
            strategy_results = {}
            
            for i, symbol in enumerate(all_symbols):
                if i % 100 == 0:
                    print(f"  Processing symbol {i+1}/{len(all_symbols)}: {symbol}")
                
                result = self.execute_strategy_on_symbol(strategy_id, symbol)
                strategy_results[symbol] = result
                
                total_executions += 1
                if result.get('success', False):
                    successful_executions += 1
                
                # Store Reliance results separately
                if symbol == 'RELIANCE':
                    self.reliance_trades[strategy_id] = result
            
            self.all_results[strategy_id] = strategy_results
        
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
        
        aggregated['overall_metrics'] = {
            'total_strategies': len(self.strategies),
            'total_symbols': len(symbol_totals),
            'total_signals_generated': np.sum(all_signals),
            'avg_signals_per_strategy': np.mean(all_signals),
            'avg_signal_percentage': np.mean(all_percentages),
            'most_active_strategy': max(aggregated['strategy_summary'].keys(), 
                                      key=lambda x: aggregated['strategy_summary'][x]['total_signals']),
            'most_active_symbol': max(symbol_totals.keys(), 
                                    key=lambda x: symbol_totals[x]['total_signals'])
        }
        
        return aggregated
    
    def get_reliance_detailed_trades(self) -> Dict[str, Any]:
        """Get detailed trade list for Reliance across all strategies"""
        print("Generating detailed Reliance trade list...")
        
        reliance_summary = {
            'total_strategies': len(self.reliance_trades),
            'total_trades': 0,
            'strategy_details': {},
            'all_trades': []
        }
        
        for strategy_id, result in self.reliance_trades.items():
            if result.get('success', False):
                trades = result.get('trades', [])
                reliance_summary['strategy_details'][strategy_id] = {
                    'strategy_name': result['strategy_name'],
                    'total_trades': len(trades),
                    'signal_percentage': result['signal_percentage'],
                    'avg_indicator_value': result['avg_indicator_value']
                }
                reliance_summary['total_trades'] += len(trades)
                reliance_summary['all_trades'].extend(trades)
        
        # Sort all trades by date index
        reliance_summary['all_trades'].sort(key=lambda x: x['date_index'])
        
        return reliance_summary
    
    def export_results(self):
        """Export all results to files"""
        print("Exporting results...")
        
        # Export aggregated results
        with open('ehlers_massive_execution_aggregated.json', 'w') as f:
            json.dump(self.aggregated_results, f, indent=2)
        
        # Export Reliance trades
        reliance_trades = self.get_reliance_detailed_trades()
        with open('ehlers_reliance_trades.json', 'w') as f:
            json.dump(reliance_trades, f, indent=2)
        
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
        report.append("OVERALL METRICS:")
        report.append(f"  Total Strategies: {overall['total_strategies']}")
        report.append(f"  Total Symbols: {overall['total_symbols']}")
        report.append(f"  Total Signals Generated: {overall['total_signals_generated']:,}")
        report.append(f"  Average Signals per Strategy: {overall['avg_signals_per_strategy']:.1f}")
        report.append(f"  Average Signal Percentage: {overall['avg_signal_percentage']:.2f}%")
        report.append(f"  Most Active Strategy: {overall['most_active_strategy']}")
        report.append(f"  Most Active Symbol: {overall['most_active_symbol']}")
        report.append("")
        
        # Top 10 strategies by signal count
        report.append("TOP 10 STRATEGIES BY SIGNAL COUNT:")
        strategy_signals = [(k, v['total_signals']) for k, v in self.aggregated_results['strategy_summary'].items()]
        strategy_signals.sort(key=lambda x: x[1], reverse=True)
        
        for i, (strategy_id, signal_count) in enumerate(strategy_signals[:10]):
            strategy_name = self.aggregated_results['strategy_summary'][strategy_id]['strategy_name']
            report.append(f"  {i+1:2d}. {strategy_id}: {signal_count:,} signals ({strategy_name})")
        report.append("")
        
        # Top 10 symbols by signal count
        report.append("TOP 10 SYMBOLS BY SIGNAL COUNT:")
        symbol_signals = [(k, v['total_signals']) for k, v in self.aggregated_results['symbol_summary'].items()]
        symbol_signals.sort(key=lambda x: x[1], reverse=True)
        
        for i, (symbol, signal_count) in enumerate(symbol_signals[:10]):
            report.append(f"  {i+1:2d}. {symbol}: {signal_count:,} signals")
        report.append("")
        
        # Reliance summary
        reliance_trades = self.get_reliance_detailed_trades()
        report.append("RELIANCE TRADING SUMMARY:")
        report.append(f"  Total Strategies: {reliance_trades['total_strategies']}")
        report.append(f"  Total Trades: {reliance_trades['total_trades']}")
        report.append("")
        
        report.append("RELIANCE STRATEGY BREAKDOWN:")
        for strategy_id, details in reliance_trades['strategy_details'].items():
            report.append(f"  {strategy_id}: {details['total_trades']} trades ({details['strategy_name']})")
        
        # Save report
        with open('ehlers_massive_execution_report.txt', 'w') as f:
            f.write('\n'.join(report))
        
        print("Summary report created: ehlers_massive_execution_report.txt")

def main():
    """Main function to run massive execution"""
    print("EHLERS MASSIVE EXECUTION - ALL STRATEGIES ON ALL SYMBOLS")
    print("=" * 60)
    
    # Initialize execution engine
    executor = EhlersMassiveExecution()
    
    # Execute all strategies on all symbols
    results = executor.execute_all_strategies_on_all_symbols()
    
    # Export results
    executor.export_results()
    
    print("\nMassive execution completed successfully!")
    print("Check the following files for results:")
    print("  - ehlers_massive_execution_aggregated.json")
    print("  - ehlers_reliance_trades.json")
    print("  - ehlers_massive_execution_report.txt")

if __name__ == "__main__":
    main()
