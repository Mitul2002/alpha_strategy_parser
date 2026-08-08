#!/usr/bin/env python3
"""
Enhanced Data Loader - Integrates high-performance backend with existing app
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
import polars as pl

from high_performance_backend import HighPerformanceBackend

class EnhancedDataLoader:
    """Enhanced data loader that uses the high-performance backend"""
    
    def __init__(self, data_path: str = None):
        self.backend = HighPerformanceBackend(data_path)
        self.data_cache = {}
        
    def load_stock_data(self, symbol: str) -> Optional[Dict[str, np.ndarray]]:
        """Load stock data using the high-performance backend"""
        return self.backend.load_symbol_data(symbol)
    
    def get_available_symbols(self) -> List[str]:
        """Get list of all available symbols"""
        return self.backend.get_available_symbols()
    
    def execute_strategy_with_metrics(self, strategy: str, symbols: List[str] = None) -> Dict[str, Any]:
        """Execute strategy and return comprehensive metrics"""
        return self.backend.execute_strategy(strategy, symbols)
    
    def get_performance_summary(self, results: Dict[str, Any]) -> str:
        """Get formatted performance summary"""
        return self.backend.get_performance_summary(results)
    
    def get_stockwise_dataframe(self, results: Dict[str, Any]) -> pd.DataFrame:
        """Get stockwise metrics as DataFrame"""
        return self.backend.get_stockwise_dataframe(results)
    
    def analyze_strategy_performance(self, strategy: str, symbols: List[str] = None) -> Dict[str, Any]:
        """Complete strategy analysis with all metrics"""
        print(f"🚀 Analyzing strategy: {strategy[:60]}...")
        
        # Execute strategy
        results = self.execute_strategy_with_metrics(strategy, symbols)
        
        # Generate summary
        summary = self.get_performance_summary(results)
        
        # Get DataFrame
        df = self.get_stockwise_dataframe(results)
        
        return {
            'results': results,
            'summary': summary,
            'dataframe': df,
            'aggregated_metrics': results.get('aggregated_metrics', {}),
            'stockwise_metrics': results.get('stockwise_metrics', [])
        }
    
    def batch_analyze_strategies(self, strategies: List[str], symbols: List[str] = None) -> Dict[str, Any]:
        """Analyze multiple strategies in batch"""
        batch_results = {}
        
        for i, strategy in enumerate(strategies, 1):
            print(f"📊 Analyzing strategy {i}/{len(strategies)}: {strategy[:50]}...")
            
            try:
                analysis = self.analyze_strategy_performance(strategy, symbols)
                batch_results[strategy] = analysis
            except Exception as e:
                print(f"❌ Error analyzing strategy {i}: {e}")
                batch_results[strategy] = {'error': str(e)}
        
        return batch_results
    
    def get_top_performing_stocks(self, results: Dict[str, Any], metric: str = 'Total_Return', top_n: int = 10) -> pd.DataFrame:
        """Get top performing stocks by specified metric"""
        df = self.get_stockwise_dataframe(results)
        if df.empty:
            return df
        
        return df.nlargest(top_n, metric)
    
    def get_strategy_comparison(self, batch_results: Dict[str, Any]) -> pd.DataFrame:
        """Compare multiple strategies"""
        comparison_data = []
        
        for strategy, analysis in batch_results.items():
            if 'error' in analysis:
                continue
            
            results = analysis.get('results', {})
            aggregated = results.get('aggregated_metrics', {})
            
            if 'overall' in aggregated:
                overall = aggregated['overall']
                comparison_data.append({
                    'Strategy': strategy[:50] + "..." if len(strategy) > 50 else strategy,
                    'Total_Signals': overall['total_signals'],
                    'Avg_Return': overall['avg_return'],
                    'Win_Rate': overall['win_rate'],
                    'Sharpe_Ratio': overall['sharpe_ratio'],
                    'Sortino_Ratio': overall['sortino_ratio'],
                    'Max_Drawdown': overall['max_drawdown'],
                    'Total_Return': overall['total_return']
                })
        
        return pd.DataFrame(comparison_data).sort_values('Sharpe_Ratio', ascending=False)

# Example usage
if __name__ == "__main__":
    # Test the enhanced data loader
    loader = EnhancedDataLoader()
    
    # Test strategies
    test_strategies = [
        "ema(close, 50) > ema(close, 200)",
        "rsi(close, 14) > 70",
        "macd(close, 12, 26, 9) > 0"
    ]
    
    # Test symbols
    test_symbols = ["RELIANCE", "INFY", "BHARTIARTL", "HDFCBANK"]
    
    print("Testing Enhanced Data Loader...")
    
    # Single strategy analysis
    analysis = loader.analyze_strategy_performance(test_strategies[0], test_symbols)
    print(analysis['summary'])
    print("\nTop performing stocks:")
    print(analysis['dataframe'].head())
    
    # Batch analysis
    print("\n" + "="*60)
    print("BATCH ANALYSIS")
    print("="*60)
    
    batch_results = loader.batch_analyze_strategies(test_strategies, test_symbols)
    comparison_df = loader.get_strategy_comparison(batch_results)
    print("\nStrategy Comparison:")
    print(comparison_df)
