#!/usr/bin/env python3
"""
High Performance Backend for Alpha Strategy Parser
Integrates the fast Polars-based engine with comprehensive metrics
"""

import json
import time
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import polars as pl
import numpy as np
import pandas as pd
from datetime import datetime

from simple_parser import SimpleStrategyParser
from strategy_executor import StrategyExecutor
from function_registry import FunctionRegistry

class HighPerformanceBackend:
    """High-performance backend using Polars and vectorized operations"""
    
    def __init__(self, data_path: str = None):
        self.parser = SimpleStrategyParser()
        self.executor = StrategyExecutor()
        self.function_registry = FunctionRegistry()
        
        # Set data path
        if data_path is None:
            # Use the partitioned parquet data
            current_dir = Path(__file__).parent.parent.parent
            self.data_path = current_dir / "context" / "rsi_forward_returns" / "data_partitioned"
        else:
            self.data_path = Path(data_path)
        
        # Cache for loaded data
        self.data_cache = {}
        
    def _extract_symbol_name(self, file_path: Path) -> str:
        """Extract clean symbol name from parquet file path"""
        stem = file_path.stem
        try:
            parsed_tuple = ast.literal_eval(stem)
            if isinstance(parsed_tuple, tuple) and len(parsed_tuple) > 0:
                return parsed_tuple[0]
        except (ValueError, SyntaxError):
            pass
        return stem
    
    def load_symbol_data(self, symbol: str) -> Optional[Dict[str, np.ndarray]]:
        """Load data for a specific symbol"""
        if symbol in self.data_cache:
            return self.data_cache[symbol]
        
        # Find the parquet file for this symbol
        parquet_files = list(self.data_path.glob('*.parquet'))
        symbol_file = None
        
        for file_path in parquet_files:
            if self._extract_symbol_name(file_path) == symbol:
                symbol_file = file_path
                break
        
        if symbol_file is None:
            print(f"Warning: No data found for symbol {symbol}")
            return None
        
        try:
            df = pl.read_parquet(symbol_file)
            
            # Convert to dictionary format expected by executor
            data_dict = {
                'datetime': df['datetime'].to_numpy(),
                'open': df['open'].to_numpy(),
                'high': df['high'].to_numpy(),
                'low': df['low'].to_numpy(),
                'close': df['close'].to_numpy(),
                'volume': df['volume'].to_numpy()
            }
            
            # Cache the data
            self.data_cache[symbol] = data_dict
            return data_dict
            
        except Exception as e:
            print(f"Error loading data for {symbol}: {e}")
            return None
    
    def get_available_symbols(self) -> List[str]:
        """Get list of all available symbols"""
        parquet_files = list(self.data_path.glob('*.parquet'))
        symbols = []
        for file_path in parquet_files:
            symbol = self._extract_symbol_name(file_path)
            if symbol:
                symbols.append(symbol)
        return sorted(symbols)
    
    def execute_strategy(self, strategy: str, symbols: List[str] = None) -> Dict[str, Any]:
        """Execute strategy on specified symbols or all symbols"""
        if symbols is None:
            symbols = self.get_available_symbols()
        
        results = {
            'strategy': strategy,
            'symbols_processed': 0,
            'total_signals': 0,
            'execution_time': 0,
            'symbol_results': {},
            'aggregated_metrics': {},
            'stockwise_metrics': []
        }
        
        start_time = time.time()
        
        # Parse strategy once
        parsed = self.parser.parse(strategy)
        if not parsed:
            results['error'] = "Failed to parse strategy"
            return results
        
        # Process each symbol
        for symbol in symbols:
            data = self.load_symbol_data(symbol)
            if data is None:
                continue
            
            try:
                # Execute strategy
                signals = self.executor.execute(parsed, data)
                if signals is None:
                    continue
                
                # Count signals
                signal_indices = np.where(signals)[0]
                signal_count = len(signal_indices)
                
                if signal_count > 0:
                    # Calculate returns for this symbol
                    symbol_metrics = self._calculate_symbol_metrics(
                        data, signals, symbol
                    )
                    results['symbol_results'][symbol] = symbol_metrics
                    results['stockwise_metrics'].append(symbol_metrics)
                
                results['symbols_processed'] += 1
                results['total_signals'] += signal_count
                
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                continue
        
        results['execution_time'] = time.time() - start_time
        
        # Calculate aggregated metrics
        if results['stockwise_metrics']:
            results['aggregated_metrics'] = self._calculate_aggregated_metrics(
                results['stockwise_metrics']
            )
        
        return results
    
    def _calculate_symbol_metrics(self, data: Dict[str, np.ndarray], signals: np.ndarray, symbol: str) -> Dict[str, Any]:
        """Calculate comprehensive metrics for a single symbol"""
        signal_indices = np.where(signals)[0]
        
        if len(signal_indices) == 0:
            return {
                'symbol': symbol,
                'total_signals': 0,
                'total_return': 0.0,
                'avg_return': 0.0,
                'win_rate': 0.0,
                'sharpe_ratio': 0.0,
                'sortino_ratio': 0.0,
                'information_ratio': 0.0,
                'max_runup': 0.0,
                'avg_std_dev': 0.0,
                'max_drawdown': 0.0,
                'best_return': 0.0,
                'worst_return': 0.0
            }
        
        # Calculate forward returns for different periods
        forward_periods = [1, 5, 10, 20]  # 1 day, 1 week, 2 weeks, 1 month
        returns_by_period = {}
        
        for period in forward_periods:
            returns = []
            for idx in signal_indices:
                if idx + period < len(data['close']):
                    entry_price = data['close'][idx]
                    exit_price = data['close'][idx + period]
                    ret = (exit_price - entry_price) / entry_price
                    returns.append(ret)
            
            if returns:
                returns_by_period[period] = np.array(returns)
        
        # Calculate metrics for each period
        metrics = {
            'symbol': symbol,
            'total_signals': len(signal_indices),
            'forward_periods': {}
        }
        
        for period, returns in returns_by_period.items():
            if len(returns) == 0:
                continue
            
            period_metrics = {
                'avg_return': float(np.mean(returns)),
                'win_rate': float(np.mean(returns > 0)),
                'sharpe_ratio': self._calculate_sharpe_ratio(returns),
                'sortino_ratio': self._calculate_sortino_ratio(returns),
                'information_ratio': self._calculate_information_ratio(returns),
                'max_runup': float(np.max(returns)),
                'avg_std_dev': float(np.std(returns)),
                'max_drawdown': self._calculate_max_drawdown(returns),
                'best_return': float(np.max(returns)),
                'worst_return': float(np.min(returns)),
                'total_return': float(np.sum(returns))
            }
            
            metrics['forward_periods'][period] = period_metrics
        
        # Use 1-day forward returns for overall metrics
        if 1 in returns_by_period:
            main_returns = returns_by_period[1]
            metrics.update({
                'total_return': float(np.sum(main_returns)),
                'avg_return': float(np.mean(main_returns)),
                'win_rate': float(np.mean(main_returns > 0)),
                'sharpe_ratio': self._calculate_sharpe_ratio(main_returns),
                'sortino_ratio': self._calculate_sortino_ratio(main_returns),
                'information_ratio': self._calculate_information_ratio(main_returns),
                'max_runup': float(np.max(main_returns)),
                'avg_std_dev': float(np.std(main_returns)),
                'max_drawdown': self._calculate_max_drawdown(main_returns),
                'best_return': float(np.max(main_returns)),
                'worst_return': float(np.min(main_returns))
            })
        
        return metrics
    
    def _calculate_aggregated_metrics(self, stockwise_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregated metrics across all symbols"""
        if not stockwise_metrics:
            return {}
        
        # Aggregate by forward period
        aggregated = {}
        
        # Get all forward periods
        all_periods = set()
        for metrics in stockwise_metrics:
            if 'forward_periods' in metrics:
                all_periods.update(metrics['forward_periods'].keys())
        
        for period in sorted(all_periods):
            period_metrics = []
            for metrics in stockwise_metrics:
                if 'forward_periods' in metrics and period in metrics['forward_periods']:
                    period_metrics.append(metrics['forward_periods'][period])
            
            if period_metrics:
                aggregated[period] = {
                    'avg_return': float(np.mean([m['avg_return'] for m in period_metrics])),
                    'win_rate': float(np.mean([m['win_rate'] for m in period_metrics])),
                    'sharpe_ratio': float(np.mean([m['sharpe_ratio'] for m in period_metrics])),
                    'sortino_ratio': float(np.mean([m['sortino_ratio'] for m in period_metrics])),
                    'information_ratio': float(np.mean([m['information_ratio'] for m in period_metrics])),
                    'max_runup': float(np.mean([m['max_runup'] for m in period_metrics])),
                    'avg_std_dev': float(np.mean([m['avg_std_dev'] for m in period_metrics])),
                    'max_drawdown': float(np.mean([m['max_drawdown'] for m in period_metrics])),
                    'best_return': float(np.max([m['best_return'] for m in period_metrics])),
                    'worst_return': float(np.min([m['worst_return'] for m in period_metrics])),
                    'total_return': float(np.sum([m['total_return'] for m in period_metrics])),
                    'total_signals': int(np.sum([m.get('total_signals', 0) for m in stockwise_metrics if 'forward_periods' in m and period in m['forward_periods']]))
                }
        
        # Overall aggregated metrics (using 1-day forward returns)
        overall_metrics = []
        for metrics in stockwise_metrics:
            if 'avg_return' in metrics:
                overall_metrics.append(metrics)
        
        if overall_metrics:
            aggregated['overall'] = {
                'avg_return': float(np.mean([m['avg_return'] for m in overall_metrics])),
                'win_rate': float(np.mean([m['win_rate'] for m in overall_metrics])),
                'sharpe_ratio': float(np.mean([m['sharpe_ratio'] for m in overall_metrics])),
                'sortino_ratio': float(np.mean([m['sortino_ratio'] for m in overall_metrics])),
                'information_ratio': float(np.mean([m['information_ratio'] for m in overall_metrics])),
                'max_runup': float(np.mean([m['max_runup'] for m in overall_metrics])),
                'avg_std_dev': float(np.mean([m['avg_std_dev'] for m in overall_metrics])),
                'max_drawdown': float(np.mean([m['max_drawdown'] for m in overall_metrics])),
                'best_return': float(np.max([m['best_return'] for m in overall_metrics])),
                'worst_return': float(np.min([m['worst_return'] for m in overall_metrics])),
                'total_return': float(np.sum([m['total_return'] for m in overall_metrics])),
                'total_signals': int(np.sum([m['total_signals'] for m in overall_metrics]))
            }
        
        return aggregated
    
    def _calculate_sharpe_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) == 0 or np.std(returns) == 0:
            return 0.0
        return float((np.mean(returns) - risk_free_rate/252) / np.std(returns) * np.sqrt(252))
    
    def _calculate_sortino_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio"""
        if len(returns) == 0:
            return 0.0
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            return float(np.mean(returns) / np.std(returns) * np.sqrt(252))
        downside_deviation = np.std(downside_returns)
        if downside_deviation == 0:
            return 0.0
        return float((np.mean(returns) - risk_free_rate/252) / downside_deviation * np.sqrt(252))
    
    def _calculate_information_ratio(self, returns: np.ndarray, benchmark_return: float = 0.0) -> float:
        """Calculate Information ratio"""
        if len(returns) == 0 or np.std(returns) == 0:
            return 0.0
        excess_returns = returns - benchmark_return
        return float(np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252))
    
    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Calculate maximum drawdown"""
        if len(returns) == 0:
            return 0.0
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return float(np.min(drawdown))
    
    def get_performance_summary(self, results: Dict[str, Any]) -> str:
        """Generate a formatted performance summary"""
        if not results.get('aggregated_metrics'):
            return "No performance data available"
        
        summary = []
        summary.append("🚀 STRATEGY PERFORMANCE SUMMARY")
        summary.append("=" * 50)
        summary.append(f"Strategy: {results['strategy'][:80]}...")
        summary.append(f"Symbols Processed: {results['symbols_processed']}")
        summary.append(f"Total Signals: {results['total_signals']:,}")
        summary.append(f"Execution Time: {results['execution_time']:.2f}s")
        summary.append("")
        
        # Overall metrics
        if 'overall' in results['aggregated_metrics']:
            overall = results['aggregated_metrics']['overall']
            summary.append("📊 OVERALL METRICS")
            summary.append("-" * 30)
            summary.append(f"Avg Return: {overall['avg_return']:.4f}")
            summary.append(f"Win Rate: {overall['win_rate']:.2%}")
            summary.append(f"Sharpe Ratio: {overall['sharpe_ratio']:.3f}")
            summary.append(f"Sortino Ratio: {overall['sortino_ratio']:.3f}")
            summary.append(f"Information Ratio: {overall['information_ratio']:.3f}")
            summary.append(f"Max Runup: {overall['max_runup']:.4f}")
            summary.append(f"Avg Std Dev: {overall['avg_std_dev']:.4f}")
            summary.append(f"Max Drawdown: {overall['max_drawdown']:.4f}")
            summary.append(f"Best Return: {overall['best_return']:.4f}")
            summary.append(f"Worst Return: {overall['worst_return']:.4f}")
            summary.append(f"Total Return: {overall['total_return']:.4f}")
            summary.append("")
        
        # Performance by forward period
        summary.append("📈 PERFORMANCE BY FORWARD PERIOD")
        summary.append("-" * 40)
        for period in sorted([k for k in results['aggregated_metrics'].keys() if k != 'overall']):
            metrics = results['aggregated_metrics'][period]
            summary.append(f"Period {period} days:")
            summary.append(f"  Avg Return: {metrics['avg_return']:.4f}")
            summary.append(f"  Win Rate: {metrics['win_rate']:.2%}")
            summary.append(f"  Sharpe: {metrics['sharpe_ratio']:.3f}")
            summary.append(f"  Total Signals: {metrics['total_signals']:,}")
            summary.append("")
        
        return "\n".join(summary)
    
    def get_stockwise_dataframe(self, results: Dict[str, Any]) -> pd.DataFrame:
        """Convert stockwise metrics to pandas DataFrame"""
        if not results.get('stockwise_metrics'):
            return pd.DataFrame()
        
        # Flatten the metrics for DataFrame
        rows = []
        for metrics in results['stockwise_metrics']:
            row = {
                'Symbol': metrics['symbol'],
                'Total_Signals': metrics['total_signals'],
                'Total_Return': metrics.get('total_return', 0.0),
                'Avg_Return': metrics.get('avg_return', 0.0),
                'Win_Rate': metrics.get('win_rate', 0.0),
                'Sharpe_Ratio': metrics.get('sharpe_ratio', 0.0),
                'Sortino_Ratio': metrics.get('sortino_ratio', 0.0),
                'Information_Ratio': metrics.get('information_ratio', 0.0),
                'Max_Runup': metrics.get('max_runup', 0.0),
                'Avg_Std_Dev': metrics.get('avg_std_dev', 0.0),
                'Max_Drawdown': metrics.get('max_drawdown', 0.0),
                'Best_Return': metrics.get('best_return', 0.0),
                'Worst_Return': metrics.get('worst_return', 0.0)
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        return df.sort_values('Total_Return', ascending=False)

# Example usage and testing
if __name__ == "__main__":
    # Test the backend
    backend = HighPerformanceBackend()
    
    # Test with a simple strategy
    test_strategy = "ema(close, 50) > ema(close, 200)"
    test_symbols = ["RELIANCE", "INFY", "BHARTIARTL", "HDFCBANK"]
    
    print("Testing High Performance Backend...")
    results = backend.execute_strategy(test_strategy, test_symbols)
    
    print(backend.get_performance_summary(results))
    print("\nStockwise DataFrame:")
    df = backend.get_stockwise_dataframe(results)
    print(df)
