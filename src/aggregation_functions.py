import numpy as np
from typing import Dict, List, Optional, Union, Tuple
from multi_timeframe_loader import MultiTimeframeLoader

class AggregationFunctions:
    """Frequency-based aggregation functions for strategy analysis"""
    
    def __init__(self, data_loader: MultiTimeframeLoader):
        self.data_loader = data_loader
    
    def min(self, data: np.ndarray, period: int = 1, exclude_current: bool = True) -> np.ndarray:
        """Get minimum value over the last n periods"""
        if period <= 1:
            return data
        
        result = np.full_like(data, np.nan)
        offset = 1 if exclude_current else 0
        
        for i in range(period + offset - 1, len(data)):
            start_idx = i - period - offset + 1
            end_idx = i - offset + 1
            result[i] = np.min(data[start_idx:end_idx])
        
        return result
    
    def max(self, data: np.ndarray, period: int = 1, exclude_current: bool = True) -> np.ndarray:
        """Get maximum value over the last n periods"""
        if period <= 1:
            return data
        
        result = np.full_like(data, np.nan)
        offset = 1 if exclude_current else 0
        
        for i in range(period + offset - 1, len(data)):
            start_idx = i - period - offset + 1
            end_idx = i - offset + 1
            result[i] = np.max(data[start_idx:end_idx])
        
        return result
    
    def count(self, data: np.ndarray, period: int = 1, exclude_current: bool = True) -> np.ndarray:
        """Count non-zero/non-nan values over the last n periods"""
        if period <= 1:
            return np.ones_like(data)
        
        result = np.full_like(data, np.nan)
        offset = 1 if exclude_current else 0
        
        for i in range(period + offset - 1, len(data)):
            start_idx = i - period - offset + 1
            end_idx = i - offset + 1
            result[i] = np.sum(~np.isnan(data[start_idx:end_idx]))
        
        return result
    
    def countstreak(self, data: np.ndarray, condition: str = 'positive', 
                    period: int = 1, exclude_current: bool = True) -> np.ndarray:
        """Count consecutive streaks meeting a condition over the last n periods"""
        if period <= 1:
            return np.ones_like(data)
        
        result = np.full_like(data, np.nan)
        offset = 1 if exclude_current else 0
        
        for i in range(period + offset - 1, len(data)):
            start_idx = i - period - offset + 1
            end_idx = i - offset + 1
            window = data[start_idx:end_idx]
            
            if condition == 'positive':
                streak = self._count_consecutive_positive(window)
            elif condition == 'negative':
                streak = self._count_consecutive_negative(window)
            elif condition == 'above_zero':
                streak = self._count_consecutive_above(window, 0)
            elif condition == 'below_zero':
                streak = self._count_consecutive_below(window, 0)
            else:
                streak = 0
            
            result[i] = streak
        
        return result
    
    def abs(self, data: np.ndarray) -> np.ndarray:
        """Get absolute values"""
        return np.abs(data)
    
    def ceil(self, data: np.ndarray) -> np.ndarray:
        """Ceiling function"""
        return np.ceil(data)
    
    def floor(self, data: np.ndarray) -> np.ndarray:
        """Floor function"""
        return np.floor(data)
    
    def round(self, data: np.ndarray, decimals: int = 0) -> np.ndarray:
        """Round to specified decimal places"""
        return np.round(data, decimals)
    
    def square(self, data: np.ndarray) -> np.ndarray:
        """Square the values"""
        return np.square(data)
    
    def n_days_ago(self, data: Dict[str, np.ndarray], n: int, 
                   exclude_current: bool = True) -> np.ndarray:
        """Get data from n days ago"""
        if 'timeframe' not in data:
            raise ValueError("Data must include timeframe information")
        
        timeframe = data['timeframe']
        if timeframe != 'daily':
            # Convert to daily equivalent
            conversion_factor = self.data_loader.get_timeframe_conversion_factor(timeframe, 'daily')
            n = n * conversion_factor
        
        result = self.data_loader.get_n_periods_ago(data, n, exclude_current)
        if result is None:
            return np.full(len(data['close']), np.nan)
        
        return result['close']
    
    def n_weeks_ago(self, data: Dict[str, np.ndarray], n: int, 
                    exclude_current: bool = True) -> np.ndarray:
        """Get data from n weeks ago"""
        if 'timeframe' not in data:
            raise ValueError("Data must include timeframe information")
        
        timeframe = data['timeframe']
        if timeframe == 'daily':
            n = n * 7
        elif timeframe == 'monthly':
            n = n * 4
        elif timeframe == 'yearly':
            n = n * 52
        
        result = self.data_loader.get_n_periods_ago(data, n, exclude_current)
        if result is None:
            return np.full(len(data['close']), np.nan)
        
        return result['close']
    
    def n_months_ago(self, data: Dict[str, np.ndarray], n: int, 
                     exclude_current: bool = True) -> np.ndarray:
        """Get data from n months ago"""
        if 'timeframe' not in data:
            raise ValueError("Data must include timeframe information")
        
        timeframe = data['timeframe']
        if timeframe == 'daily':
            n = n * 30
        elif timeframe == 'weekly':
            n = n * 4
        elif timeframe == 'yearly':
            n = n * 12
        
        result = self.data_loader.get_n_periods_ago(data, n, exclude_current)
        if result is None:
            return np.full(len(data['close']), np.nan)
        
        return result['close']
    
    def n_years_ago(self, data: Dict[str, np.ndarray], n: int, 
                    exclude_current: bool = True) -> np.ndarray:
        """Get data from n years ago"""
        if 'timeframe' not in data:
            raise ValueError("Data must include timeframe information")
        
        timeframe = data['timeframe']
        if timeframe == 'daily':
            n = n * 365
        elif timeframe == 'weekly':
            n = n * 52
        elif timeframe == 'monthly':
            n = n * 12
        
        result = self.data_loader.get_n_periods_ago(data, n, exclude_current)
        if result is None:
            return np.full(len(data['close']), np.nan)
        
        return result['close']
    
    def _count_consecutive_positive(self, data: np.ndarray) -> int:
        """Count consecutive positive values from the end"""
        count = 0
        for i in range(len(data) - 1, -1, -1):
            if data[i] > 0:
                count += 1
            else:
                break
        return count
    
    def _count_consecutive_negative(self, data: np.ndarray) -> int:
        """Count consecutive negative values from the end"""
        count = 0
        for i in range(len(data) - 1, -1, -1):
            if data[i] < 0:
                count += 1
            else:
                break
        return count
    
    def _count_consecutive_above(self, data: np.ndarray, threshold: float) -> int:
        """Count consecutive values above threshold from the end"""
        count = 0
        for i in range(len(data) - 1, -1, -1):
            if data[i] > threshold:
                count += 1
            else:
                break
        return count
    
    def _count_consecutive_below(self, data: np.ndarray, threshold: float) -> int:
        """Count consecutive values below threshold from the end"""
        count = 0
        for i in range(len(data) - 1, -1, -1):
            if data[i] < threshold:
                count += 1
            else:
                break
        return count

def test_aggregation_functions():
    """Test the aggregation functions"""
    print("🧪 Testing Aggregation Functions")
    print("=" * 50)
    
    try:
        # Create mock data loader
        from unittest.mock import Mock
        mock_loader = Mock()
        mock_loader.get_timeframe_conversion_factor.return_value = 1
        
        # Create aggregation functions
        agg_funcs = AggregationFunctions(mock_loader)
        
        # Test data
        test_data = np.array([1.5, -2.3, 3.7, -1.2, 4.8, 0.0, -3.1, 2.9])
        test_data_with_timeframe = {
            'timeframe': 'daily',
            'close': test_data
        }
        
        print(f"📊 Test data: {test_data}")
        
        # Test basic functions
        print(f"\n🔢 Basic Functions:")
        print(f"   abs: {agg_funcs.abs(test_data)}")
        print(f"   ceil: {agg_funcs.ceil(test_data)}")
        print(f"   floor: {agg_funcs.floor(test_data)}")
        print(f"   round: {agg_funcs.round(test_data, 1)}")
        print(f"   square: {agg_funcs.square(test_data)}")
        
        # Test aggregation functions
        print(f"\n📈 Aggregation Functions (period=3):")
        print(f"   min: {agg_funcs.min(test_data, 3)}")
        print(f"   max: {agg_funcs.max(test_data, 3)}")
        print(f"   count: {agg_funcs.count(test_data, 3)}")
        
        # Test streak functions
        print(f"\n🔥 Streak Functions (period=5):")
        print(f"   positive streak: {agg_funcs.countstreak(test_data, 'positive', 5)}")
        print(f"   negative streak: {agg_funcs.countstreak(test_data, 'negative', 5)}")
        
        print(f"\n🎉 Aggregation Functions Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_aggregation_functions() 