#!/usr/bin/env python3
"""
Run EMA50>EMA200 + RSI40 strategy on Reliance data
"""

import sys
import os
sys.path.append('alpha_strategy_parser/src')

import pandas as pd
import numpy as np
from datetime import datetime

def calculate_rsi(prices, period=14):
    """Calculate RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_ema(prices, period):
    """Calculate EMA"""
    return prices.ewm(span=period).mean()

def run_strategy():
    """Run the strategy on Reliance data"""
    print("�� RUNNING EMA50>EMA200 + RSI40 STRATEGY ON RELIANCE DATA")
    print("=" * 60)
    print()
    
    # Load Reliance data
    print("Loading Reliance data...")
    data = pd.read_csv('data/RELIANCE.csv')
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values('date').reset_index(drop=True)
    
    print(f"Data loaded: {len(data)} rows")
    print(f"Date range: {data['date'].min()} to {data['date'].max()}")
    print()
    
    # Calculate indicators
    print("Calculating indicators...")
    data['rsi_14'] = calculate_rsi(data['close'], 14)
    data['ema_50'] = calculate_ema(data['close'], 50)
    data['ema_200'] = calculate_ema(data['close'], 200)
    
    # Strategy logic: RSI(14) crossover 40 and EMA(50) > EMA(200)
    print("Applying strategy logic...")
    
    # RSI crossover 40 (RSI crosses above 40)
    data['rsi_cross_up'] = (data['rsi_14'] > 40) & (data['rsi_14'].shift(1) <= 40)
    
    # EMA condition
    data['ema_condition'] = data['ema_50'] > data['ema_200']
    
    # Entry signal
    data['entry_signal'] = data['rsi_cross_up'] & data['ema_condition']
    
    # Find entry points
    entry_points = data[data['entry_signal']].copy()
    
    print(f"Found {len(entry_points)} entry signals")
    print()
    
    # Generate trades (entry today, exit next day)
    trades = []
    for i, row in entry_points.iterrows():
        if i + 1 < len(data):  # Make sure we have next day data
            entry_date = row['date']
            entry_price = row['close']
            exit_date = data.iloc[i + 1]['date']
            exit_price = data.iloc[i + 1]['close']
            
            pnl = (exit_price - entry_price) / entry_price * 100
            
            trades.append({
                'entry_date': entry_date.strftime('%Y-%m-%d'),
                'entry_price': entry_price,
                'exit_date': exit_date.strftime('%Y-%m-%d'),
                'exit_price': exit_price,
                'pnl_percent': pnl,
                'rsi_value': row['rsi_14'],
                'ema_50_value': row['ema_50'],
                'ema_200_value': row['ema_200']
            })
    
    # Create results DataFrame
    results_df = pd.DataFrame(trades)
    
    if len(results_df) > 0:
        # Calculate performance metrics
        total_trades = len(results_df)
        winning_trades = len(results_df[results_df['pnl_percent'] > 0])
        match_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_pnl = results_df['pnl_percent'].sum()
        avg_pnl = results_df['pnl_percent'].mean()
        
        print("📊 STRATEGY PERFORMANCE")
        print("=" * 60)
        print(f"Total Trades: {total_trades}")
        print(f"Winning Trades: {winning_trades}")
        print(f"Match Rate: {match_rate:.1f}%")
        print(f"Total P&L: {total_pnl:.2f}%")
        print(f"Average P&L per Trade: {avg_pnl:.2f}%")
        print()
        
        # Save results
        results_df.to_csv('strategy_analysis_new/engine_output/reliance_ema50_ema200_rsi40_engine.csv', index=False)
        print(f"Results saved to: strategy_analysis_new/engine_output/reliance_ema50_ema200_rsi40_engine.csv")
        print()
        
        # Show first 10 trades
        print("📈 FIRST 10 TRADES")
        print("=" * 60)
        print(results_df[['entry_date', 'entry_price', 'exit_date', 'exit_price', 'pnl_percent']].head(10))
        print()
        
        # Show last 10 trades
        print("📈 LAST 10 TRADES")
        print("=" * 60)
        print(results_df[['entry_date', 'entry_price', 'exit_date', 'exit_price', 'pnl_percent']].tail(10))
        print()
        
        return results_df
    else:
        print("❌ No trades generated!")
        return pd.DataFrame()

if __name__ == "__main__":
    results = run_strategy()
    print("🚀 Strategy execution complete!")
