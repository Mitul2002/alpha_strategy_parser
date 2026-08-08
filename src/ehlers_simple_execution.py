#!/usr/bin/env python3
"""
Ehlers Simple Execution - Using proven string-based strategy approach
Based on ALL_STRATEGIES_MASTER.txt structure to avoid segfaults
"""

import numpy as np
import pandas as pd
import time
import json
import os
import sys
import gc
from pathlib import Path
from typing import Dict, List, Any, Optional
import warnings
from tqdm import tqdm
import requests
warnings.filterwarnings('ignore')

# Add the parent directory to the path to import modules
sys.path.append('/home/miso/Documents/SID/alpha_parser_project_analysis/alpha_strategy_parser/src')

class EhlersSimpleExecution:
    """Execute Ehlers strategies using the proven string-based approach"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.data_path = "../../context/rsi_forward_returns/data_partitioned"
        
        # Define 50 Ehlers strategies as simple strings (like ALL_STRATEGIES_MASTER.txt)
        self.strategies = self.create_ehlers_strategies()
        
        # Results storage
        self.all_results = {}
        self.strategy_folders = {}
        
        print(f"Initialized with {len(self.strategies)} Ehlers strategies")
    
    def create_ehlers_strategies(self) -> List[str]:
        """Create 50 Ehlers strategies as simple strings"""
        strategies = [
            # Fisher Transform strategies
            "fisher_transform(close, 10) > 0",
            "fisher_transform(close, 10) crossover 0",
            "fisher_transform(close, 10) > 0.5",
            "fisher_transform(close, 10) < -0.5",
            "fisher_transform(close, 10) > fisher_transform(close, 10)[1]",
            
            # Instantaneous Trendline strategies
            "instantaneous_trendline(close, 0.07) > close",
            "instantaneous_trendline(close, 0.07) crossover close",
            "instantaneous_trendline(close, 0.07) > instantaneous_trendline(close, 0.07)[1]",
            "close > instantaneous_trendline(close, 0.07)",
            "instantaneous_trendline(close, 0.07) > sma(close, 20)",
            
            # CG Oscillator strategies
            "cg_oscillator(close, 10) > 0",
            "cg_oscillator(close, 10) crossover 0",
            "cg_oscillator(close, 10) > 0.1",
            "cg_oscillator(close, 10) < -0.1",
            "cg_oscillator(close, 10) > cg_oscillator(close, 10)[1]",
            
            # Relative Vigor Index strategies
            "relative_vigor_index(close, 10) > 0",
            "relative_vigor_index(close, 10) crossover 0",
            "relative_vigor_index(close, 10) > 0.5",
            "relative_vigor_index(close, 10) < -0.5",
            "relative_vigor_index(close, 10) > relative_vigor_index(close, 10)[1]",
            
            # Cyber Cycle Oscillator strategies
            "cyber_cycle_oscillator(close, 10) > 0",
            "cyber_cycle_oscillator(close, 10) crossover 0",
            "cyber_cycle_oscillator(close, 10) > 0.2",
            "cyber_cycle_oscillator(close, 10) < -0.2",
            "cyber_cycle_oscillator(close, 10) > cyber_cycle_oscillator(close, 10)[1]",
            
            # Decycler strategies
            "decycler(close, 40) > close",
            "decycler(close, 40) crossover close",
            "decycler(close, 40) > decycler(close, 40)[1]",
            "close > decycler(close, 40)",
            "decycler(close, 40) > sma(close, 20)",
            
            # Band Pass Filter strategies
            "band_pass_filter(close, 10, 20) > 0",
            "band_pass_filter(close, 10, 20) crossover 0",
            "band_pass_filter(close, 10, 20) > 0.1",
            "band_pass_filter(close, 10, 20) < -0.1",
            "band_pass_filter(close, 10, 20) > band_pass_filter(close, 10, 20)[1]",
            
            # Super Smoother strategies
            "super_smoother(close, 10) > close",
            "super_smoother(close, 10) crossover close",
            "super_smoother(close, 10) > super_smoother(close, 10)[1]",
            "close > super_smoother(close, 10)",
            "super_smoother(close, 10) > sma(close, 20)",
            
            # Roofing Filter strategies
            "roofing_filter(close, 40) > close",
            "roofing_filter(close, 40) crossover close",
            "roofing_filter(close, 40) > roofing_filter(close, 40)[1]",
            "close > roofing_filter(close, 40)",
            "roofing_filter(close, 40) > sma(close, 20)",
            
            # Combined strategies
            "fisher_transform(close, 10) > 0 AND instantaneous_trendline(close, 0.07) > close",
            "cg_oscillator(close, 10) > 0 AND relative_vigor_index(close, 10) > 0",
            "cyber_cycle_oscillator(close, 10) > 0 AND decycler(close, 40) > close",
            "band_pass_filter(close, 10, 20) > 0 AND super_smoother(close, 10) > close",
            "roofing_filter(close, 40) > close AND fisher_transform(close, 10) > 0"
        ]
        
        return strategies
    
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
    
    def create_strategy_folders(self):
        """Create folders for each strategy"""
        print("Creating strategy folders...")
        
        for i, strategy in enumerate(self.strategies, 1):
            # Create a safe folder name
            strategy_name = f"strategy_{i:02d}_ehlers"
            folder_path = Path(strategy_name)
            folder_path.mkdir(exist_ok=True)
            self.strategy_folders[i] = folder_path
            print(f"Created folder: {strategy_name}")
    
    def execute_strategy_on_symbol(self, strategy: str, symbol: str) -> Dict[str, Any]:
        """Execute a strategy on a symbol using the backend API"""
        try:
            # Prepare payload for backend
            payload = {
                "strategy": strategy,
                "symbols": [symbol],
                "lookahead_days": 1
            }
            
            # Call backend API
            response = requests.post(
                f"{self.backend_url}/execute-multi-lookahead",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('results'):
                    symbol_result = result['results'][0]
                    return {
                        'symbol': symbol,
                        'strategy': strategy,
                        'success': True,
                        'signals': symbol_result.get('signals', []),
                        'total_signals': len(symbol_result.get('signals', [])),
                        'trades': symbol_result.get('trades', [])
                    }
                else:
                    return {
                        'symbol': symbol,
                        'strategy': strategy,
                        'success': False,
                        'error': 'No results from backend'
                    }
            else:
                return {
                    'symbol': symbol,
                    'strategy': strategy,
                    'success': False,
                    'error': f'Backend error: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'symbol': symbol,
                'strategy': strategy,
                'success': False,
                'error': str(e)
            }
    
    def execute_all_strategies_on_all_symbols(self) -> Dict[str, Any]:
        """Execute all strategies on all symbols with progress bars"""
        print("Starting massive execution of all Ehlers strategies...")
        
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
        for strategy_idx, strategy in enumerate(tqdm(self.strategies, 
                                                   desc="Strategies", 
                                                   position=0, 
                                                   leave=True), 1):
            
            strategy_results = {}
            strategy_trades = []
            
            # Progress bar for symbols within each strategy
            for symbol in tqdm(all_symbols, 
                             desc=f"Strategy {strategy_idx}", 
                             position=1, 
                             leave=False):
                
                result = self.execute_strategy_on_symbol(strategy, symbol)
                strategy_results[symbol] = result
                
                total_executions += 1
                if result.get('success', False):
                    successful_executions += 1
                    # Collect trades for this strategy
                    strategy_trades.extend(result.get('trades', []))
            
            self.all_results[strategy_idx] = strategy_results
            
            # Save strategy-specific results
            self.save_strategy_results(strategy_idx, strategy, strategy_trades)
            
            # Memory cleanup after each strategy
            try:
                del strategy_trades
                del strategy_results
                gc.collect()
            except Exception:
                pass
        
        execution_time = time.time() - start_time
        
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
            'avg_time_per_execution': execution_time/total_executions*1000
        }
    
    def save_strategy_results(self, strategy_idx: int, strategy: str, strategy_trades: List[Dict]):
        """Save results for a specific strategy"""
        folder_path = self.strategy_folders[strategy_idx]
        
        # Create DataFrame for trades
        if strategy_trades:
            df_trades = pd.DataFrame(strategy_trades)
            
            # Save as CSV
            csv_path = folder_path / f"strategy_{strategy_idx:02d}_trades.csv"
            df_trades.to_csv(csv_path, index=False)
            
            # Save as Parquet for better performance
            parquet_path = folder_path / f"strategy_{strategy_idx:02d}_trades.parquet"
            df_trades.to_parquet(parquet_path, index=False)
            
            # Save strategy metadata
            metadata = {
                'strategy_index': strategy_idx,
                'strategy_string': strategy,
                'total_trades': len(strategy_trades),
                'unique_symbols': df_trades['symbol'].nunique() if 'symbol' in df_trades.columns else 0,
                'date_range': {
                    'start': int(df_trades['entry_date_index'].min()) if 'entry_date_index' in df_trades.columns else 0,
                    'end': int(df_trades['entry_date_index'].max()) if 'entry_date_index' in df_trades.columns else 0
                }
            }
            
            metadata_path = folder_path / f"strategy_{strategy_idx:02d}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Ensure DataFrame memory is released
            try:
                del df_trades
                gc.collect()
            except Exception:
                pass

def main():
    """Main function to run simple execution"""
    print("EHLERS SIMPLE EXECUTION - USING PROVEN STRUCTURE")
    print("=" * 60)
    
    # Initialize execution engine
    executor = EhlersSimpleExecution()
    
    # Execute all strategies on all symbols
    results = executor.execute_all_strategies_on_all_symbols()
    
    print("\nSimple execution completed successfully!")
    print("Check the following for results:")
    print("  - Individual strategy folders with trade lists")
    print("  - CSV and Parquet files for each strategy")

if __name__ == "__main__":
    main()
