#!/usr/bin/env python3
"""
Enhanced Data Loader - Full Scale Version for all ~4000 stocks
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
import polars as pl

from src.production_backend import ProductionBackend

class EnhancedDataLoaderFullScale:
    """Enhanced data loader optimized for full-scale analysis with all stocks"""
    
    def __init__(self, data_path: str = None):
        self.backend = ProductionBackend(data_path)
        
    def get_all_symbols(self) -> List[str]:
        """Get all available symbols"""
        return self.backend.get_all_symbols()
    
    def analyze_strategy_full_scale(self, strategy: str) -> Dict[str, Any]:
        """Analyze strategy on all available stocks"""
        try:
            print(f"🚀 FULL-SCALE STRATEGY ANALYSIS")
            print(f"==================================================")
            print(f"Strategy: {strategy[:50]}...")
            
            # Execute full-scale analysis
            results = self.backend.analyze_strategy_full_scale(strategy)
            
            # Get summary
            summary = self.backend.get_performance_summary(results)
            
            # Get DataFrame
            df = self.get_stockwise_dataframe(results)
            
            return {
                'results': results,
                'summary': summary,
                'dataframe': df,
                'aggregated_metrics': results.get('aggregated_metrics', {}),
                'stockwise_metrics': results.get('stockwise_metrics', []),
                'performance_stats': results.get('performance_stats', {})
            }
            
        except Exception as e:
            print(f"❌ Error in full-scale analysis: {e}")
            raise e
    
    def get_performance_summary(self, results: Dict[str, Any]) -> str:
        """Get performance summary"""
        return self.backend.get_performance_summary(results)
    
    def get_stockwise_dataframe(self, results: Dict[str, Any]) -> pd.DataFrame:
        """Convert stockwise metrics to DataFrame"""
        stockwise_metrics = results.get('stockwise_metrics', [])
        
        if not stockwise_metrics:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(stockwise_metrics)
        
        # Round numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].round(6)
        
        return df
