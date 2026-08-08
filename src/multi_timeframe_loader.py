import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

class MultiTimeframeLoader:
    """Data loader for multiple timeframes with historical data access"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            # Use absolute path to the data_multi_timeframe directory
            current_dir = Path(__file__).parent.parent.parent
            self.base_path = current_dir / "data_multi_timeframe"
        else:
            self.base_path = Path(base_path)
        self.data_cache = {}
        self.timeframes = ['daily', 'weekly', 'monthly', 'yearly']
        
        # Validate timeframes exist
        for timeframe in self.timeframes:
            timeframe_dir = self.base_path / timeframe
            if not timeframe_dir.exists():
                raise ValueError(f"Timeframe directory not found: {timeframe_dir}")
    
    def load_stock_data(self, symbol: str, timeframe: str = 'daily') -> Optional[Dict[str, np.ndarray]]:
        """Load stock data for specific timeframe"""
        cache_key = f"{symbol}_{timeframe}"
        
        if cache_key in self.data_cache:
            return self.data_cache[cache_key]
        
        if timeframe not in self.timeframes:
            raise ValueError(f"Invalid timeframe: {timeframe}. Available: {self.timeframes}")
        
        csv_file = self.base_path / timeframe / f"{symbol}.csv"
        if not csv_file.exists():
            print(f"Warning: {csv_file} not found")
            return None
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Convert to numpy arrays
            data = {
                'timeframe': timeframe,
                'date': df['date'].values,
                'open': df['open'].values.astype(np.float64),
                'high': df['high'].values.astype(np.float64),
                'low': df['low'].values.astype(np.float64),
                'close': df['close'].values.astype(np.float64),
                'volume': df['volume'].values.astype(np.float64)
            }
            
            # Cache the data
            self.data_cache[cache_key] = data
            return data
            
        except Exception as e:
            print(f"Error loading {symbol} ({timeframe}): {e}")
            return None
    
    def load_multiple_timeframes(self, symbol: str) -> Dict[str, Dict[str, np.ndarray]]:
        """Load data for all timeframes for a single symbol"""
        result = {}
        for timeframe in self.timeframes:
            data = self.load_stock_data(symbol, timeframe)
            if data is not None:
                result[timeframe] = data
        return result
    
    def get_available_symbols(self, timeframe: str = 'daily') -> List[str]:
        """Get list of available stock symbols for a timeframe"""
        if timeframe not in self.timeframes:
            raise ValueError(f"Invalid timeframe: {timeframe}")
        
        timeframe_dir = self.base_path / timeframe
        csv_files = list(timeframe_dir.glob("*.csv"))
        return [f.stem for f in csv_files]
    
    def get_data_info(self, symbol: str, timeframe: str = 'daily') -> Optional[Dict]:
        """Get information about stock data for a timeframe"""
        data = self.load_stock_data(symbol, timeframe)
        if data is None:
            return None
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'data_points': len(data['close']),
            'date_range': f"{data['date'][0]} to {data['date'][-1]}",
            'price_range': f"${data['close'].min():.2f} - ${data['close'].max():.2f}",
            'avg_volume': f"{data['volume'].mean():,.0f}"
        }
    
    def get_n_periods_ago(self, data: Dict[str, np.ndarray], n: int, 
                          exclude_current: bool = True) -> Dict[str, np.ndarray]:
        """Get data from n periods ago"""
        if n >= len(data['close']):
            return None
        
        offset = n + (1 if exclude_current else 0)
        
        result = {}
        for key, values in data.items():
            if key != 'timeframe':
                result[key] = values[:-offset] if offset > 0 else values
        
        return result
    
    def get_last_n_periods(self, data: Dict[str, np.ndarray], n: int, 
                           exclude_current: bool = True) -> Dict[str, np.ndarray]:
        """Get last n periods of data"""
        if n >= len(data['close']):
            return data
        
        offset = 1 if exclude_current else 0
        
        result = {}
        for key, values in data.items():
            if key != 'timeframe':
                result[key] = values[-(n+offset):-offset] if offset > 0 else values[-n:]
        
        return result
    
    def get_period_range(self, data: Dict[str, np.ndarray], start_periods_ago: int, 
                        end_periods_ago: int, exclude_current: bool = True) -> Dict[str, np.ndarray]:
        """Get data from a specific range of periods ago"""
        if start_periods_ago < end_periods_ago:
            start_periods_ago, end_periods_ago = end_periods_ago, start_periods_ago
        
        if start_periods_ago >= len(data['close']):
            return None
        
        offset = 1 if exclude_current else 0
        start_idx = -(start_periods_ago + offset)
        end_idx = -(end_periods_ago + offset)
        
        result = {}
        for key, values in data.items():
            if key != 'timeframe':
                result[key] = values[start_idx:end_idx]
        
        return result
    
    def get_timeframe_conversion_factor(self, from_timeframe: str, to_timeframe: str) -> int:
        """Get conversion factor between timeframes"""
        conversion_map = {
            'daily': 1,
            'weekly': 7,
            'monthly': 30,
            'yearly': 365
        }
        
        if from_timeframe not in conversion_map or to_timeframe not in conversion_map:
            raise ValueError(f"Invalid timeframe: {from_timeframe} or {to_timeframe}")
        
        return conversion_map[to_timeframe] // conversion_map[from_timeframe]

def test_multi_timeframe_loader():
    """Test the multi-timeframe loader"""
    print("🧪 Testing Multi-Timeframe Loader")
    print("=" * 50)
    
    try:
        loader = MultiTimeframeLoader()
        
        # Test loading different timeframes
        symbol = 'RELIANCE'
        timeframes = ['daily', 'weekly', 'monthly', 'yearly']
        
        for timeframe in timeframes:
            print(f"\n📊 Testing {timeframe} data for {symbol}")
            
            data = loader.load_stock_data(symbol, timeframe)
            if data:
                info = loader.get_data_info(symbol, timeframe)
                print(f"   ✅ Loaded: {info['data_points']} records")
                print(f"   📅 Range: {info['date_range']}")
                print(f"   💰 Price: {info['price_range']}")
            else:
                print(f"   ❌ Failed to load")
        
        # Test historical data access
        print(f"\n📈 Testing Historical Data Access")
        daily_data = loader.load_stock_data('RELIANCE', 'daily')
        
        if daily_data:
            # Test n periods ago
            n_periods_ago = loader.get_n_periods_ago(daily_data, 5)
            print(f"   ✅ 5 periods ago: {len(n_periods_ago['close'])} records")
            
            # Test last n periods
            last_n = loader.get_last_n_periods(daily_data, 10)
            print(f"   ✅ Last 10 periods: {len(last_n['close'])} records")
            
            # Test period range
            period_range = loader.get_period_range(daily_data, 20, 10)
            print(f"   ✅ Period range 10-20: {len(period_range['close'])} records")
        
        print(f"\n🎉 Multi-Timeframe Loader Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multi_timeframe_loader() 