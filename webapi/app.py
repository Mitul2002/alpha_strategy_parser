import os
import sys
import json
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from function_registry import FunctionRegistry
from simple_parser import SimpleStrategyParser

def safe_float(value):
    """Convert value to float, handling NaN and inf values"""
    if np.isnan(value) or np.isinf(value):
        return 0.0
    return float(value)

from strategy_executor import StrategyExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Alpha Strategy Parser API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
registry = FunctionRegistry()
parser = SimpleStrategyParser()
executor = StrategyExecutor()

# Helper function to convert numpy types to Python types for JSON serialization
def convert_numpy_types(obj):
    """Recursively convert numpy types to Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif pd.isna(obj):
        return None
    else:
        return obj

class StrategyRequest(BaseModel):
    strategy: str
    lookahead_periods: List[int] = [7]
    include_trades: bool = False

class IndicatorRequest(BaseModel):
    symbol: str
    indicators: List[str]

@app.get("/")
async def root():
    return {"message": "Alpha Strategy Parser API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/symbols")
async def get_symbols():
    """Get list of available symbols"""
    try:
        data_root_env = os.getenv("DATA_PARTITIONED_PATH")
        default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'context', 'rsi_forward_returns', 'data_partitioned'))
        data_path = Path(data_root_env) if data_root_env else Path(default_path)
        
        symbols = []
        for p in data_path.glob("*.parquet"):
            stem = p.stem.replace("('", "").replace("',)", "").upper()
            symbols.append(stem)
        
        return {"symbols": sorted(symbols), "count": len(symbols)}
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ohlcv/{symbol}")
async def get_ohlcv(symbol: str):
    """Get OHLCV data for a symbol"""
    try:
        data_root_env = os.getenv("DATA_PARTITIONED_PATH")
        default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'context', 'rsi_forward_returns', 'data_partitioned'))
        data_path = Path(data_root_env) if data_root_env else Path(default_path)
        
        target = symbol.strip().upper()
        parquet_path = None
        
        for p in data_path.glob("*.parquet"):
            stem = p.stem.replace("('", "").replace("',)", "").upper()
            if stem == target:
                parquet_path = p
                break
        
        if parquet_path is None:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        df = pd.read_parquet(parquet_path)
        
        # Convert to dict format expected by frontend
        data = {
            "symbol": target,
            "data": df.to_dict('records')
        }
        
        return data
        
    except Exception as e:
        logger.error(f"Error loading OHLCV for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _log_run(strategy: str, aggregated_metrics: dict, stockwise_metrics: list, backend_version: str):
    """Log strategy execution results"""
    try:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"strategy_run_{timestamp}.json"
        
        log_data = {
            "timestamp": timestamp,
            "strategy": strategy,
            "backend_version": backend_version,
            "aggregated_metrics": aggregated_metrics,
            "stockwise_metrics": stockwise_metrics
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)
            
    except Exception as e:
        print(f"⚠️ Failed to log run: {e}")

def extract_basic_indicator_specs(strategy: str) -> List[str]:
    """Extract basic indicator specifications from strategy string"""
    basic_indicators = []
    
    # Common TA-Lib indicators
    ta_lib_patterns = [
        r'sma\([^)]+\)', r'ema\([^)]+\)', r'wma\([^)]+\)', r'dema\([^)]+\)', r'tema\([^)]+\)',
        r'trima\([^)]+\)', r'kama\([^)]+\)', r'mama\([^)]+\)', r'vwma\([^)]+\)', r't3\([^)]+\)',
        r'macd\([^)]+\)', r'macd_ext\([^)]+\)', r'ppo\([^)]+\)', r'ppo_ext\([^)]+\)',
        r'stoch\([^)]+\)', r'stochf\([^)]+\)', r'stochrsi\([^)]+\)',
        r'rsi\([^)]+\)', r'willr\([^)]+\)', r'cci\([^)]+\)', r'ultosc\([^)]+\)', r'trange\([^)]+\)',
        r'atr\([^)]+\)', r'natr\([^)]+\)', r'true_range\([^)]+\)',
        r'ad\([^)]+\)', r'adosc\([^)]+\)', r'obv\([^)]+\)', r'obv_ema\([^)]+\)',
        r'bb_upper\([^)]+\)', r'bb_middle\([^)]+\)', r'bb_lower\([^)]+\)', r'bb_width\([^)]+\)', r'bb_percent\([^)]+\)',
        r'stddev\([^)]+\)', r'var\([^)]+\)', r'median_price\([^)]+\)', r'typical_price\([^)]+\)', r'weighted_close\([^)]+\)',
        r'ht_dcperiod\([^)]+\)', r'ht_dcphase\([^)]+\)', r'ht_phasor\([^)]+\)', r'ht_sine\([^)]+\)', r'ht_trendmode\([^)]+\)',
        r'linearreg\([^)]+\)', r'linearreg_angle\([^)]+\)', r'linearreg_intercept\([^)]+\)', r'linearreg_slope\([^)]+\)',
        r'tsf\([^)]+\)', r'correl\([^)]+\)', r'beta\([^)]+\)', r'linearreg_slope\([^)]+\)',
        r'min\([^)]+\)', r'max\([^)]+\)', r'minmax\([^)]+\)', r'minmaxindex\([^)]+\)',
        r'sum\([^)]+\)', r'add\([^)]+\)', r'sub\([^)]+\)', r'mult\([^)]+\)', r'div\([^)]+\)',
        r'acos\([^)]+\)', r'asin\([^)]+\)', r'atan\([^)]+\)', r'ceil\([^)]+\)', r'cos\([^)]+\)', r'cosh\([^)]+\)',
        r'exp\([^)]+\)', r'floor\([^)]+\)', r'ln\([^)]+\)', r'log10\([^)]+\)', r'sin\([^)]+\)', r'sinh\([^)]+\)',
        r'sqrt\([^)]+\)', r'tan\([^)]+\)', r'tanh\([^)]+\)', r'abs\([^)]+\)', r'neg\([^)]+\)',
        r'cdl2crows\([^)]+\)', r'cdl3blackcrows\([^)]+\)', r'cdl3inside\([^)]+\)', r'cdl3linestrike\([^)]+\)',
        r'cdl3outside\([^)]+\)', r'cdl3starsinsouth\([^)]+\)', r'cdl3whitesoldiers\([^)]+\)', r'cdlabandonedbaby\([^)]+\)',
        r'cdladvanceblock\([^)]+\)', r'cdlbelthold\([^)]+\)', r'cdlbreakaway\([^)]+\)', r'cdlclosingmarubozu\([^)]+\)',
        r'cdlconcealbabyswall\([^)]+\)', r'cdlcounterattack\([^)]+\)', r'cdldarkcloudcover\([^)]+\)', r'cdldoji\([^)]+\)',
        r'cdldojistar\([^)]+\)', r'cdldragonflydoji\([^)]+\)', r'cdlengulfing\([^)]+\)', r'cdleveningdojistar\([^)]+\)',
        r'cdleveningstar\([^)]+\)', r'cdlgapsidesidewhite\([^)]+\)', r'cdlgravestonedoji\([^)]+\)', r'cdlhammer\([^)]+\)',
        r'cdlhangingman\([^)]+\)', r'cdlharami\([^)]+\)', r'cdlharamicross\([^)]+\)', r'cdlhighwave\([^)]+\)',
        r'cdlhikkake\([^)]+\)', r'cdlhikkakemod\([^)]+\)', r'cdlhomingpigeon\([^)]+\)', r'cdlidentical3crows\([^)]+\)',
        r'cdlinneck\([^)]+\)', r'cdlinvertedhammer\([^)]+\)', r'cdlkicking\([^)]+\)', r'cdlkickingbylength\([^)]+\)',
        r'cdlladderbottom\([^)]+\)', r'cdllongleggeddoji\([^)]+\)', r'cdllongline\([^)]+\)', r'cdlmarubozu\([^)]+\)',
        r'cdlmatchinglow\([^)]+\)', r'cdlmathold\([^)]+\)', r'cdlmorningdojistar\([^)]+\)', r'cdlmorningstar\([^)]+\)',
        r'cdlonneck\([^)]+\)', r'cdlpiercing\([^)]+\)', r'cdlrickshawman\([^)]+\)', r'cdlrisefall3methods\([^)]+\)',
        r'cdlseparatinglines\([^)]+\)', r'cdlshootingstar\([^)]+\)', r'cdlshortline\([^)]+\)', r'cdlspinningtop\([^)]+\)',
        r'cdlstalledpattern\([^)]+\)', r'cdlsticksandwich\([^)]+\)', r'cdltakuri\([^)]+\)', r'cdltasukigap\([^)]+\)',
        r'cdlthrusting\([^)]+\)', r'cdltristar\([^)]+\)', r'cdlunique3river\([^)]+\)', r'cdlupsidegap2crows\([^)]+\)',
        r'cdlxsidegap3methods\([^)]+\)', r'adx\([^)]+\)', r'adxr\([^)]+\)', r'apo\([^)]+\)', r'aroon\([^)]+\)', r'aroonosc\([^)]+\)',
        r'bop\([^)]+\)', r'cmf\([^)]+\)', r'dx\([^)]+\)', r'mfi\([^)]+\)', r'minus_di\([^)]+\)', r'minus_dm\([^)]+\)',
        r'plus_di\([^)]+\)', r'plus_dm\([^)]+\)', r'roc\([^)]+\)', r'rocp\([^)]+\)', r'rocr\([^)]+\)', r'rocr100\([^)]+\)',
        r'trix\([^)]+\)', r'ultosc\([^)]+\)', r'willr\([^)]+\)'
    ]
    
    import re
    for pattern in ta_lib_patterns:
        matches = re.findall(pattern, strategy, re.IGNORECASE)
        basic_indicators.extend(matches)
    
    return list(set(basic_indicators))  # Remove duplicates

@app.post("/execute-multi-lookahead")
async def execute_multi_lookahead(request: StrategyRequest):
    """Execute strategy with multiple lookahead periods"""
    try:
        strategy = request.strategy.strip()
        lookahead_periods = request.lookahead_periods
        include_trades = request.include_trades
        
        print(f"🚀 MULTI-LOOKAHEAD ANALYSIS: {strategy[:50]}... with periods: {lookahead_periods}")
        
        # Extract basic indicator specs
        indicator_specs = extract_basic_indicator_specs(strategy)
        
        # Get data path
        data_root_env = os.getenv("DATA_PARTITIONED_PATH")
        default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'context', 'rsi_forward_returns', 'data_partitioned'))
        data_path = Path(data_root_env) if data_root_env else Path(default_path)
        
        # Get sample files (limit to avoid timeout)
        sample_files = list(data_path.glob("*.parquet"))
        print(f"📊 Found {len(sample_files)} symbols to process")
        
        # Initialize results storage
        all_results = {str(period): [] for period in lookahead_periods}
        trades_payload = []
        
        for file_path in sample_files:
            try:
                df = pd.read_parquet(file_path)
                if len(df) < 100:  # Skip files with insufficient data
                    continue
                
                # Set context for registry
                registry.set_context(df["date"].values if "date" in df.columns else df["Date"].values if "Date" in df.columns else df.index.values)
                
                # Parse strategy
                parsed = parser.parse(strategy)
                if parsed is None:
                    print(f"❌ Failed to parse strategy: {strategy}")
                    continue
                
                # Execute strategy
                print(f"Executing strategy on {file_path.name}, data shape: {df.shape}")
                result = executor.execute(parsed, df)
                print(f"Signals generated: {len(result)} signals, sum: {np.sum(result)}")
                    
                # Handle different result types from executor
                # Convert to numpy array if it's a pandas Series, list, or other type
                if hasattr(result, 'values'):  # pandas Series or DataFrame
                    signals = result.values
                elif isinstance(result, list):
                    signals = np.array(result)
                elif isinstance(result, np.ndarray):
                    signals = result
                else:
                    signals = np.array([])
                
                # Extract symbol name
                symbol = file_path.stem.replace("('", "").replace("',)", "").upper()
                
                total_signals = np.sum(signals)
                print(f"🔍 DEBUG: {symbol} - Total signals: {total_signals}, Signal type: {type(signals)}, Signal shape: {signals.shape if hasattr(signals, 'shape') else 'N/A'}")
                
                if total_signals == 0:
                    print(f"⚠️  DEBUG: {symbol} - Skipping due to 0 signals")
                    continue
                else:
                    print(f"✅ DEBUG: {symbol} - Processing {total_signals} signals")
                
                # Calculate forward returns for each lookahead period
                for lookahead in lookahead_periods:
                    lookahead_key = str(lookahead)
                    print(f"🔍 DEBUG: {symbol} - Processing lookahead {lookahead}")
                    
                    # Calculate forward returns
                    close_prices = df["close"].values
                    returns = []
                    signal_count = 0
                    
                    for i in range(len(signals)):
                        if signals[i] and i + lookahead < len(close_prices):
                            signal_count += 1
                            entry_price = close_prices[i]
                            exit_price = close_prices[i + lookahead]
                            forward_return = (exit_price - entry_price) / entry_price
                            returns.append(forward_return)
                    
                    print(f"🔍 DEBUG: {symbol} - Lookahead {lookahead}: {signal_count} valid signals, {len(returns)} returns calculated")
                    
                    if not returns:
                        print(f"⚠️  DEBUG: {symbol} - Lookahead {lookahead}: No returns calculated, skipping")
                        continue
                    
                    # Calculate performance metrics
                    avg_return = np.mean(returns)
                    win_rate = np.mean([r > 0 for r in returns])
                    sharpe_ratio = avg_return / np.std(returns) if np.std(returns) > 0 else 0.0
                    sortino_ratio = avg_return / np.std([r for r in returns if r < 0]) if any(r < 0 for r in returns) else 0.0
                    information_ratio = avg_return / np.std(returns) if np.std(returns) > 0 else 0.0
                    std_dev = np.std(returns)
                    max_runup = np.max(returns)
                    
                    print(f"�� DEBUG: {symbol} - Lookahead {lookahead}: avg_return={avg_return:.4f}, win_rate={win_rate:.4f}, sharpe={sharpe_ratio:.4f}, returns_count={len(returns)}")
                    
                    # Create payload with safe float conversion
                    payload = {
                        'symbol': symbol,
                        'total_signals': int(total_signals),
                        'avg_return': safe_float(avg_return),
                        'win_rate': safe_float(win_rate),
                        'sharpe_ratio': safe_float(sharpe_ratio),
                        'sortino_ratio': safe_float(sortino_ratio),
                        'information_ratio': safe_float(information_ratio),
                        'std_dev': safe_float(std_dev),
                        'max_runup': safe_float(max_runup)
                    }
                    
                    # Add trades if requested
                    if include_trades and total_signals > 0:
                        try:
                            # Get signal indices
                            signals_bool = np.array(signals, dtype=bool)
                            if np.any(signals_bool):
                                # Get date column
                                date_col = None
                                for col in ['date', 'Date', 'DATE']:
                                    if col in df.columns:
                                        date_col = col
                                        break
                                
                                dates_np = df[date_col].to_numpy() if date_col else None
                                close_np = df["close"].to_numpy()
                                
                                # Get entry indices
                                entry_idx = np.where(signals_bool)[0]
                                entries = []
                                
                                for idx_val in entry_idx:
                                    entry_date = str(dates_np[idx_val]) if dates_np is not None else None
                                    entries.append({
                                        "entry_index": int(idx_val),
                                        "entry_date": entry_date,
                                        "entry_price": float(close_np[idx_val])
                                    })
                                
                                payload['trades'] = entries
                                
                                # Add to trades_payload for the first lookahead period
                                if lookahead == lookahead_periods[0]:
                                    trades_payload.extend(entries)
                                    
                        except Exception as _te:
                            pass
                    
                    all_results[lookahead_key].append(payload)
                    
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
                continue
        
        # Aggregate results across all lookahead periods
        aggregated_metrics = {
            "strategy": strategy,
            "lookahead_periods": lookahead_periods,
            "total_symbols_processed": len(sample_files),
            "total_signals": 0,
            "average_return": 0.0,
            "avg_win_rate": 0.0,
            "avg_sharpe": 0.0,
            "avg_sortino": 0.0,
            "avg_information_ratio": 0.0,
            "avg_std_dev": 0.0,
            "max_runup": 0.0,
            "avg_signals_per_day": 0.0,
        }
        
        # Calculate aggregated metrics (using the first lookahead period for overall stats)
        print(f"🔍 DEBUG: Aggregation - lookahead_periods: {lookahead_periods}")
        print(f"🔍 DEBUG: Aggregation - all_results keys: {list(all_results.keys())}")
        for key, results in all_results.items():
            print(f"🔍 DEBUG: Aggregation - {key}: {len(results)} results")
        
        if lookahead_periods and len(all_results[str(lookahead_periods[0])]) > 0:
            first_period_results = all_results[str(lookahead_periods[0])]
            print(f"🔍 DEBUG: Aggregation - Using {len(first_period_results)} results for aggregation")
            
            # Convert all numpy values to Python types
            total_signals = sum(r['total_signals'] for r in first_period_results)
            avg_return = safe_float(np.mean([r['avg_return'] for r in first_period_results]))
            avg_win_rate = safe_float(np.mean([r['win_rate'] for r in first_period_results]))
            avg_sharpe = safe_float(np.mean([r['sharpe_ratio'] for r in first_period_results]))
            avg_sortino = safe_float(np.mean([r['sortino_ratio'] for r in first_period_results]))
            avg_information_ratio = safe_float(np.mean([r['information_ratio'] for r in first_period_results]))
            avg_std_dev = safe_float(np.mean([r['std_dev'] for r in first_period_results]))
            max_runup = safe_float(np.max([r['max_runup'] for r in first_period_results]))
            avg_signals_per_day = safe_float(np.mean([r['total_signals'] for r in first_period_results]) / 252)
            
            aggregated_metrics.update({
                "total_signals": int(total_signals),
                "average_return": avg_return,
                "avg_win_rate": avg_win_rate,
                "avg_sharpe": avg_sharpe,
                "avg_sortino": avg_sortino,
                "avg_information_ratio": avg_information_ratio,
                "avg_std_dev": avg_std_dev,
                "max_runup": max_runup,
                "avg_signals_per_day": avg_signals_per_day,
            })
        
        # Log the run
        try:
            _log_run(
                strategy=strategy,
                aggregated_metrics=aggregated_metrics,
                stockwise_metrics=all_results[str(lookahead_periods[0])] if lookahead_periods else [],
                backend_version="1.0.0"
            )
        except Exception as e:
            print(f"⚠️ Failed to log run: {e}")
        
        # Prepare response with proper type conversion
        response_data = {
            "ok": True, 
            "results": {
                "aggregated_metrics": convert_numpy_types(aggregated_metrics),
                "stockwise_metrics": convert_numpy_types(all_results[str(lookahead_periods[0])] if lookahead_periods else []),
                "lookahead_results": convert_numpy_types(all_results),
                "trades_payload": convert_numpy_types(trades_payload),
                "performance_stats": {
                    'total_symbols': len(sample_files),
                    'successful_symbols': len([r for r in all_results[str(lookahead_periods[0])] if r['total_signals'] > 0]) if lookahead_periods else 0
                },
                "indicator_specs": indicator_specs,
            }
        }
        
        return response_data
        
    except Exception as e:
        print(f"❌ Error in multi-lookahead analysis: {e}")
        traceback.print_exc()
        return {"ok": False, "error": str(e)}

# ---- Indicator series endpoint (on-demand, symbol-scoped) ----
@app.get("/indicator-series")
async def indicator_series(symbol: str, indicators: str):
    try:
        # Load symbol OHLCV similar to /ohlcv
        data_root_env = os.getenv("DATA_PARTITIONED_PATH")
        default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'context', 'rsi_forward_returns', 'data_partitioned'))
        data_path = Path(data_root_env) if data_root_env else Path(default_path)
        target = symbol.strip().upper()
        parquet_path = None
        for p in data_path.glob("*.parquet"):
            stem = p.stem.replace("('", "").replace("',)", "").upper()
            if stem == target:
                parquet_path = p
                break
        if parquet_path is None:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        df = pd.read_parquet(parquet_path)
        
        # Parse indicators list
        indicator_list = [ind.strip() for ind in indicators.split(',')]
        
        # Calculate indicators
        result = {}
        for indicator in indicator_list:
            try:
                # This would need to be implemented based on your indicator calculation logic
                # For now, return placeholder
                result[indicator] = [0.0] * len(df)
            except Exception as e:
                result[indicator] = f"Error: {str(e)}"
        
        return {"symbol": target, "indicators": result}
        
    except Exception as e:
        logger.error(f"Error calculating indicators for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
