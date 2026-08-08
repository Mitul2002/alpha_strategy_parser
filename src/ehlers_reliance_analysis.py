#!/usr/bin/env python3
"""
Detailed RELIANCE Analysis - Generate comprehensive trade list for all 50 strategies
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

class RelianceAnalysis:
    """Detailed analysis of RELIANCE across all 50 Ehlers strategies"""
    
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
        
        # Load RELIANCE data
        self.reliance_data = self.load_reliance_data()
        
        print(f"Initialized with {len(self.strategies)} strategies")
        print(f"RELIANCE data: {len(self.reliance_data['close'])} days")
    
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
    
    def load_reliance_data(self) -> Dict[str, np.ndarray]:
        """Load RELIANCE OHLCV data"""
        try:
            data_path = Path(self.data_path)
            
            # Try symbol=RELIANCE/ format first
            symbol_dir = data_path / "symbol=RELIANCE"
            parquet_file = symbol_dir / "symbol=RELIANCE.parquet"
            
            if not parquet_file.exists():
                # Try tuple format
                parquet_file = data_path / "('RELIANCE',).parquet"
            
            if not parquet_file.exists():
                raise FileNotFoundError("RELIANCE data not found")
            
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
            print(f"Error loading RELIANCE data: {e}")
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
    
    def analyze_strategy_on_reliance(self, strategy_id: str) -> Dict[str, Any]:
        """Analyze a specific strategy on RELIANCE"""
        if strategy_id not in self.strategies:
            return {'error': f'Strategy {strategy_id} not found'}
        
        strategy_config = self.strategies[strategy_id]
        
        try:
            # Extract strategy configuration
            base_indicator = strategy_config['base_indicator']
            transformation = strategy_config['transformation']
            signal_type = strategy_config['signal_type']
            signal_params = strategy_config['signal_params']
            indicator_params = strategy_config['indicator_params']
            
            # Calculate enhanced indicator
            indicator_values = self.get_enhanced_indicator(
                base_indicator, transformation, self.reliance_data['close'], **indicator_params
            )
            
            # Generate signals
            signals = self.generate_signals(indicator_values, signal_type, **signal_params)
            
            # Create detailed trade list
            trade_list = []
            signal_indices = np.where(signals)[0]
            
            for idx in signal_indices:
                if idx < len(self.reliance_data['close']):
                    trade = {
                        'date_index': int(idx),
                        'price': float(self.reliance_data['close'][idx]),
                        'indicator_value': float(indicator_values[idx]) if not np.isnan(indicator_values[idx]) else 0.0,
                        'signal_type': signal_type,
                        'strategy_id': strategy_id,
                        'strategy_name': strategy_config['name']
                    }
                    trade_list.append(trade)
            
            # Calculate metrics
            signal_count = len(signal_indices)
            total_days = len(self.reliance_data['close'])
            signal_percentage = (signal_count / total_days * 100) if total_days > 0 else 0
            
            result = {
                'strategy_id': strategy_id,
                'strategy_name': strategy_config['name'],
                'base_indicator': base_indicator,
                'transformation': transformation,
                'signal_type': signal_type,
                'total_signals': signal_count,
                'total_days': total_days,
                'signal_percentage': signal_percentage,
                'avg_indicator_value': float(np.nanmean(indicator_values)),
                'indicator_std': float(np.nanstd(indicator_values)),
                'indicator_min': float(np.nanmin(indicator_values)),
                'indicator_max': float(np.nanmax(indicator_values)),
                'trades': trade_list,
                'success': True
            }
            
            return result
            
        except Exception as e:
            return {
                'strategy_id': strategy_id,
                'error': str(e),
                'success': False
            }
    
    def analyze_all_strategies_on_reliance(self) -> Dict[str, Any]:
        """Analyze all 50 strategies on RELIANCE"""
        print("Analyzing all 50 strategies on RELIANCE...")
        
        results = {}
        total_trades = 0
        
        for strategy_id, strategy_config in self.strategies.items():
            print(f"Analyzing {strategy_id}: {strategy_config['name']}")
            
            result = self.analyze_strategy_on_reliance(strategy_id)
            results[strategy_id] = result
            
            if result.get('success', False):
                total_trades += result['total_signals']
        
        # Create summary
        summary = {
            'reliance_data_info': {
                'total_days': len(self.reliance_data['close']),
                'price_range': {
                    'min': float(np.min(self.reliance_data['close'])),
                    'max': float(np.max(self.reliance_data['close'])),
                    'current': float(self.reliance_data['close'][-1])
                },
                'data_period': f"{len(self.reliance_data['close'])} trading days"
            },
            'strategy_analysis': results,
            'overall_summary': {
                'total_strategies': len(self.strategies),
                'successful_strategies': sum(1 for r in results.values() if r.get('success', False)),
                'total_trades_generated': total_trades,
                'avg_trades_per_strategy': total_trades / len(self.strategies)
            }
        }
        
        return summary
    
    def export_reliance_analysis(self, analysis_results: Dict[str, Any]):
        """Export RELIANCE analysis results"""
        print("Exporting RELIANCE analysis...")
        
        # Export full analysis
        with open('ehlers_reliance_complete_analysis.json', 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        # Create detailed trade list
        all_trades = []
        for strategy_id, result in analysis_results['strategy_analysis'].items():
            if result.get('success', False):
                for trade in result['trades']:
                    all_trades.append(trade)
        
        # Sort by date index
        all_trades.sort(key=lambda x: x['date_index'])
        
        # Export trade list
        trade_list = {
            'reliance_trades': all_trades,
            'total_trades': len(all_trades),
            'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('ehlers_reliance_trade_list.json', 'w') as f:
            json.dump(trade_list, f, indent=2)
        
        # Create summary report
        self.create_reliance_report(analysis_results, all_trades)
        
        print("RELIANCE analysis exported successfully!")
    
    def create_reliance_report(self, analysis_results: Dict[str, Any], all_trades: List[Dict]):
        """Create comprehensive RELIANCE report"""
        report = []
        report.append("RELIANCE COMPREHENSIVE ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # RELIANCE data info
        data_info = analysis_results['reliance_data_info']
        report.append("RELIANCE DATA INFORMATION:")
        report.append(f"  Total Trading Days: {data_info['total_days']:,}")
        report.append(f"  Price Range: ₹{data_info['price_range']['min']:.2f} - ₹{data_info['price_range']['max']:.2f}")
        report.append(f"  Current Price: ₹{data_info['price_range']['current']:.2f}")
        report.append("")
        
        # Overall summary
        summary = analysis_results['overall_summary']
        report.append("OVERALL ANALYSIS SUMMARY:")
        report.append(f"  Total Strategies Analyzed: {summary['total_strategies']}")
        report.append(f"  Successful Strategies: {summary['successful_strategies']}")
        report.append(f"  Total Trades Generated: {summary['total_trades_generated']:,}")
        report.append(f"  Average Trades per Strategy: {summary['avg_trades_per_strategy']:.1f}")
        report.append("")
        
        # Top 10 strategies by trade count
        strategy_trades = []
        for strategy_id, result in analysis_results['strategy_analysis'].items():
            if result.get('success', False):
                strategy_trades.append((strategy_id, result['strategy_name'], result['total_signals']))
        
        strategy_trades.sort(key=lambda x: x[2], reverse=True)
        
        report.append("TOP 10 STRATEGIES BY TRADE COUNT:")
        for i, (strategy_id, strategy_name, trade_count) in enumerate(strategy_trades[:10]):
            report.append(f"  {i+1:2d}. {strategy_id}: {trade_count:,} trades ({strategy_name})")
        report.append("")
        
        # Strategy categories summary
        categories = {
            'Base Indicators (1-9)': strategy_trades[:9],
            'Stochasticized (10-18)': strategy_trades[9:18],
            'Fisherized (19-27)': strategy_trades[18:27],
            'Combined Transform (28-36)': strategy_trades[27:36],
            'Extreme Signals (37-45)': strategy_trades[36:45],
            'Special Combinations (46-50)': strategy_trades[45:50]
        }
        
        report.append("STRATEGY CATEGORIES SUMMARY:")
        for category, strategies in categories.items():
            if strategies:
                total_trades = sum(s[2] for s in strategies)
                avg_trades = total_trades / len(strategies)
                report.append(f"  {category}: {total_trades:,} total trades, {avg_trades:.1f} avg per strategy")
        report.append("")
        
        # Sample trades
        report.append("SAMPLE TRADES (First 20):")
        for i, trade in enumerate(all_trades[:20]):
            report.append(f"  {i+1:2d}. Day {trade['date_index']:4d}: Price ₹{trade['price']:8.2f}, "
                         f"Indicator {trade['indicator_value']:8.3f} ({trade['strategy_name']})")
        report.append("")
        
        # Save report
        with open('ehlers_reliance_analysis_report.txt', 'w') as f:
            f.write('\n'.join(report))
        
        print("RELIANCE analysis report created: ehlers_reliance_analysis_report.txt")

def main():
    """Main function to run RELIANCE analysis"""
    print("RELIANCE COMPREHENSIVE ANALYSIS - ALL 50 STRATEGIES")
    print("=" * 60)
    
    # Initialize analysis
    analyzer = RelianceAnalysis()
    
    if analyzer.reliance_data is None:
        print("Could not load RELIANCE data. Exiting.")
        return
    
    # Analyze all strategies
    results = analyzer.analyze_all_strategies_on_reliance()
    
    # Export results
    analyzer.export_reliance_analysis(results)
    
    print("\nRELIANCE analysis completed successfully!")
    print("Check the following files for results:")
    print("  - ehlers_reliance_complete_analysis.json")
    print("  - ehlers_reliance_trade_list.json")
    print("  - ehlers_reliance_analysis_report.txt")

if __name__ == "__main__":
    main()
