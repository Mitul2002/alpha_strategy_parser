import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional

class DataLoader:
    def __init__(self, data_path: str = None):
        if data_path is None:
            # Use absolute path to the data directory
            current_dir = Path(__file__).parent.parent.parent
            self.data_path = current_dir / "data"
        else:
            self.data_path = Path(data_path)
        self.data_cache = {}
        
    def load_stock_data(self, symbol: str) -> Optional[Dict[str, np.ndarray]]:
        """Load stock data from CSV file"""
        if symbol in self.data_cache:
            return self.data_cache[symbol]
        
        csv_file = self.data_path / f"{symbol}.csv"
        if not csv_file.exists():
            print(f"Warning: {csv_file} not found")
            return None
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Convert to numpy arrays
            data = {
                'date': df['date'].values,
                'open': df['open'].values.astype(np.float64),
                'high': df['high'].values.astype(np.float64),
                'low': df['low'].values.astype(np.float64),
                'close': df['close'].values.astype(np.float64),
                'volume': df['volume'].values.astype(np.float64)
            }
            
            # Cache the data
            self.data_cache[symbol] = data
            return data
            
        except Exception as e:
            print(f"Error loading {symbol}: {e}")
            return None
    
    def load_multiple_stocks(self, symbols: List[str]) -> Dict[str, Dict[str, np.ndarray]]:
        """Load multiple stock data"""
        stocks_data = {}
        for symbol in symbols:
            data = self.load_stock_data(symbol)
            if data is not None:
                stocks_data[symbol] = data
        return stocks_data
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available stock symbols"""
        csv_files = list(self.data_path.glob("*.csv"))
        return [f.stem for f in csv_files]
    
    def get_data_info(self, symbol: str) -> Optional[Dict]:
        """Get information about stock data"""
        data = self.load_stock_data(symbol)
        if data is None:
            return None
        
        return {
            'symbol': symbol,
            'data_points': len(data['close']),
            'date_range': f"{data['date'][0]} to {data['date'][-1]}",
            'price_range': f"${data['close'].min():.2f} - ${data['close'].max():.2f}",
            'avg_volume': f"{data['volume'].mean():,.0f}"
        } 