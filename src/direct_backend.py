#!/usr/bin/env python3
"""
Direct backend for frontend integration - bypasses FastAPI
"""

import json
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from enhanced_data_loader_full_scale import EnhancedDataLoaderFullScale

def execute_strategy_full_scale(strategy: str):
    """Execute strategy on all available stocks with comprehensive metrics"""
    try:
        # Initialize the full-scale data loader
        loader = EnhancedDataLoaderFullScale()
        
        # Execute strategy on all symbols
        analysis = loader.analyze_strategy_full_scale(strategy)
        
        return {
            "ok": True,
            "results": analysis
        }
        
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Test the backend
    result = execute_strategy_full_scale("ema(close, 50) > ema(close, 200)")
    print(json.dumps(result, indent=2))
