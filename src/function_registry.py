import numpy as np
import talib
from typing import Dict, Any, Callable, List, Optional

class FunctionRegistry:
    """Registry for technical indicators and data access functions"""

    def __init__(self):
        self.functions = {}
        self._current_dates = None  # numpy datetime64[D]
        self._bucket_cache = {}
        self._register_functions()
    
    def set_context(self, data: Dict[str, Any]):
        """Provide per-symbol execution context for tf() bucketing. Looks for a
        'date' or 'datetime' column (in that priority order -- the real production
        parquet data uses 'datetime', which previously wasn't checked at all here,
        silently disabling tf() weekly/monthly/yearly bucketing on live data), and
        falls back to a datetime index if neither column is present."""
        try:
            dates = data.get('date')
            if dates is None:
                dates = data.get('datetime')
            if dates is None and hasattr(data, 'index'):
                index = data.index
                if np.issubdtype(getattr(index, 'dtype', np.dtype('O')), np.datetime64):
                    dates = index
            if dates is not None:
                # Ensure numpy datetime64[D]
                self._current_dates = np.asarray(dates).astype('datetime64[D]')
        except Exception:
            self._current_dates = None
    
    def _register_functions(self):
        """Register all available functions"""
        
        # Technical indicators using TA-Lib
        self.functions['rsi'] = self._rsi
        self.functions['sma'] = self._sma
        self.functions['ema'] = self._ema
        self.functions['ma'] = self._ma
        self.functions['wma'] = self._wma
        self.functions['macd'] = self._macd
        self.functions['macd_signal'] = self._macd_signal
        self.functions['macd_hist'] = self._macd_hist
        self.functions['bbands'] = self._bbands
        self.functions['bbands_upper'] = self._bbands_upper
        self.functions['bbands_lower'] = self._bbands_lower
        self.functions['bbands_middle'] = self._bbands_middle
        # New simple BB functions
        self.functions['bb_upper'] = self._bb_upper
        self.functions['bb_lower'] = self._bb_lower
        self.functions['bb_middle'] = self._bb_middle
        self.functions['stoch'] = self._stoch
        self.functions['stoch_k'] = self._stoch_k
        self.functions['stoch_d'] = self._stoch_d
        self.functions['stochrsi'] = self._stochrsi
        self.functions['stochrsi_k'] = self._stochrsi_k
        self.functions['stochrsi_d'] = self._stochrsi_d
        # Underscore variants for compatibility
        self.functions["stoch_k"] = self._stoch_k
        self.functions["stoch_d"] = self._stoch_d
        self.functions["macd_signal"] = self._macd_signal
        self.functions["macd_hist"] = self._macd_hist
        self.functions["stochrsi_k"] = self._stochrsi_k
        self.functions["stochrsi_d"] = self._stochrsi_d
        self.functions["plus_di"] = self._plus_di
        self.functions["minus_di"] = self._minus_di
        self.functions['adx'] = self._adx
        self.functions['dx'] = self._dx
        self.functions['minus_di'] = self._minus_di
        self.functions['plus_di'] = self._plus_di
        self.functions['minus_dm'] = self._minus_dm
        self.functions['plus_dm'] = self._plus_dm
        self.functions['cci'] = self._cci
        self.functions['mfi'] = self._mfi
        self.functions['willr'] = self._willr
        self.functions['sar'] = self._sar
        self.functions['atr'] = self._atr
        self.functions['natr'] = self._natr
        self.functions['trange'] = self._trange
        self.functions['obv'] = self._obv
        self.functions['mom'] = self._mom
        self.functions['roc'] = self._roc
        self.functions['cmo'] = self._cmo
        self.functions['ultosc'] = self._ultosc
        self.functions['ppo'] = self._ppo
        self.functions['stddev'] = self._stddev
        self.functions['var'] = self._var
        self.functions['linearreg'] = self._linearreg
        # Custom simple series functions
        self.functions['cum'] = self._cum
        self.functions['cumulative'] = self._cum
        # GenMoM family (time-series approximations)
        self.functions['genmom'] = self._genmom_generic
        self.functions['genmom_fip'] = self._genmom_fip
        self.functions['fip_score'] = self._fip_score_ts
        
        # Data access functions
        self.functions['open'] = self._data_access
        self.functions['high'] = self._data_access
        self.functions['low'] = self._data_access
        self.functions['close'] = self._data_access
        self.functions['volume'] = self._data_access
        
        # Aggregation functions
        self.functions['min'] = self._min
        self.functions['max'] = self._max
        self.functions['count'] = self._count
        self.functions['countstreak'] = self._countstreak
        self.functions['abs'] = self._abs
        self.functions['ceil'] = self._ceil
        self.functions['floor'] = self._floor
        self.functions['round'] = self._round
        self.functions['square'] = self._square
        
        # Historical access functions
        self.functions['n_days_ago'] = self._n_days_ago
        self.functions['n_weeks_ago'] = self._n_weeks_ago
        self.functions['n_months_ago'] = self._n_months_ago

        # Timeframe function
        self.functions['tf'] = self._tf
        
        # Crossover function (for explicit crossover calls)
        self.functions['crossover'] = self._crossover
        self.functions['n_years_ago'] = self._n_years_ago

    def get_function(self, name: str) -> Optional[Callable]:
        """Get function by name"""
        return self.functions.get(name)
    
    def list_functions(self) -> List[str]:
        """List all available function names"""
        return list(self.functions.keys())
    
    def has_function(self, name: str) -> bool:
        """Check if function exists"""
        return name in self.functions
    
    def _ensure_numeric_array(self, data, function_name: str) -> np.ndarray:
        """Helper method to ensure data is a numeric numpy array"""
        if isinstance(data, str):
            raise ValueError(f"{function_name} returned string instead of numeric array: {data}")
        
        try:
            result = np.asarray(data, dtype=np.float64)
            return result
        except (ValueError, TypeError) as e:
            raise ValueError(f"{function_name} failed to convert to numeric array: {e}")
    
    # Technical indicator implementations
    def _rsi(self, close: np.ndarray, period: int = 14) -> np.ndarray:
        """Relative Strength Index"""
        result = talib.RSI(close.astype(np.float64), timeperiod=period)
        return self._ensure_numeric_array(result, "RSI")
    
    def _sma(self, close: np.ndarray, period: int = 20) -> np.ndarray:
        """Simple Moving Average"""
        if isinstance(close, str):
            close = np.asarray([float(x) for x in close.split(',')])
        result = talib.SMA(close.astype(np.float64), timeperiod=period)
        return self._ensure_numeric_array(result, "SMA")
    
    def _ema(self, close: np.ndarray, period: int = 20) -> np.ndarray:
        """Exponential Moving Average"""
        result = talib.EMA(close.astype(np.float64), timeperiod=period)
        return self._ensure_numeric_array(result, "EMA")
    
    def _ma(self, close: np.ndarray, period: int = 20) -> np.ndarray:
        """Moving Average"""
        return talib.MA(close.astype(np.float64), timeperiod=period)
    
    def _wma(self, close: np.ndarray, period: int = 20) -> np.ndarray:
        """Weighted Moving Average"""
        return talib.WMA(close.astype(np.float64), timeperiod=period)
    
    def _macd(self, close: np.ndarray, fastperiod: int = 12, 
              slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        """MACD Line"""
        macd, signal, hist = talib.MACD(close.astype(np.float64), 
                                       fastperiod=fastperiod, 
                                       slowperiod=slowperiod, 
                                       signalperiod=signalperiod)
        return self._ensure_numeric_array(macd, "MACD")
    
    def _macd_signal(self, close: np.ndarray, fastperiod: int = 12, 
                     slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        """MACD Signal Line"""
        macd, signal, hist = talib.MACD(close.astype(np.float64), 
                                       fastperiod=fastperiod, 
                                       slowperiod=slowperiod, 
                                       signalperiod=signalperiod)
        return signal
    
    def _macd_hist(self, close: np.ndarray, fastperiod: int = 12, 
                   slowperiod: int = 26, signalperiod: int = 9) -> np.ndarray:
        """MACD Histogram"""
        macd, signal, hist = talib.MACD(close.astype(np.float64), 
                                       fastperiod=fastperiod, 
                                       slowperiod=slowperiod, 
                                       signalperiod=signalperiod)
        return hist
    
    def _bbands(self, close: np.ndarray, period: int = 20, 
                nbdevup: float = 2.0, nbdevdn: float = 2.0) -> np.ndarray:
        """Bollinger Bands (returns middle band)"""
        upper, middle, lower = talib.BBANDS(close.astype(np.float64), 
                                           timeperiod=period, 
                                           nbdevup=nbdevup, 
                                           nbdevdn=nbdevdn)
        # Ensure numeric return type
        if isinstance(middle, str):
            raise ValueError("Bollinger Bands middle returned string instead of numeric array")
        return np.asarray(middle, dtype=np.float64)
    
    def _bbands_upper(self, close: np.ndarray, period: int = 20, 
                      nbdevup: float = 2.0, nbdevdn: float = 2.0) -> np.ndarray:
        """Bollinger Bands Upper"""
        upper, middle, lower = talib.BBANDS(close.astype(np.float64), 
                                           timeperiod=period, 
                                           nbdevup=nbdevup, 
                                           nbdevdn=nbdevdn)
        # Ensure numeric return type
        if isinstance(upper, str):
            raise ValueError("Bollinger Bands upper returned string instead of numeric array")
        return np.asarray(upper, dtype=np.float64)
    
    def _bbands_lower(self, close: np.ndarray, period: int = 20, 
                      nbdevup: float = 2.0, nbdevdn: float = 2.0) -> np.ndarray:
        """Bollinger Bands Lower"""
        upper, middle, lower = talib.BBANDS(close.astype(np.float64), 
                                           timeperiod=period, 
                                           nbdevup=nbdevup, 
                                           nbdevdn=nbdevdn)
        # Ensure numeric return type
        if isinstance(lower, str):
            raise ValueError("Bollinger Bands lower returned string instead of numeric array")
        return np.asarray(lower, dtype=np.float64)
    
    def _bbands_middle(self, close: np.ndarray, period: int = 20, 
                       nbdevup: float = 2.0, nbdevdn: float = 2.0) -> np.ndarray:
        """Bollinger Bands Middle"""
        upper, middle, lower = talib.BBANDS(close.astype(np.float64), 
                                           timeperiod=period, 
                                           nbdevup=nbdevup, 
                                           nbdevdn=nbdevdn)
        # Ensure numeric return type
        if isinstance(middle, str):
            raise ValueError("Bollinger Bands middle returned string instead of numeric array")
        return np.asarray(middle, dtype=np.float64)
    
    def _bb_upper(self, close: np.ndarray, period: int = 20, nbdev: float = 2.0) -> np.ndarray:
        """Bollinger Bands Upper - Simple function"""
        upper, middle, lower = talib.BBANDS(close.astype(np.float64), 
                                           timeperiod=period, 
                                           nbdevup=nbdev, 
                                           nbdevdn=nbdev)
        # Ensure numeric return type
        if isinstance(upper, str):
            raise ValueError("BB Upper returned string instead of numeric array")
        return np.asarray(upper, dtype=np.float64)
    
    def _bb_lower(self, close: np.ndarray, period: int = 20, nbdev: float = 2.0) -> np.ndarray:
        """Bollinger Bands Lower - Simple function"""
        upper, middle, lower = talib.BBANDS(close.astype(np.float64), 
                                           timeperiod=period, 
                                           nbdevup=nbdev, 
                                           nbdevdn=nbdev)
        # Ensure numeric return type
        if isinstance(lower, str):
            raise ValueError("BB Lower returned string instead of numeric array")
        return np.asarray(lower, dtype=np.float64)
    
    def _bb_middle(self, close: np.ndarray, period: int = 20, nbdev: float = 2.0) -> np.ndarray:
        """Bollinger Bands Middle - Simple function"""
        upper, middle, lower = talib.BBANDS(close.astype(np.float64), 
                                           timeperiod=period, 
                                           nbdevup=nbdev, 
                                           nbdevdn=nbdev)
        # Ensure numeric return type
        if isinstance(middle, str):
            raise ValueError("BB Middle returned string instead of numeric array")
        return np.asarray(middle, dtype=np.float64)
    
    def _stoch(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
               fastk_period: int = 14, slowk_period: int = 3, 
               slowd_period: int = 3) -> np.ndarray:
        """Stochastic Oscillator (returns %K)"""
        slowk, slowd = talib.STOCH(high.astype(np.float64), 
                                   low.astype(np.float64), 
                                   close.astype(np.float64), 
                                   fastk_period=fastk_period, 
                                   slowk_period=slowk_period, 
                                   slowd_period=slowd_period)
        return slowk
    
    def _stoch_k(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                 fastk_period: int = 14, slowk_period: int = 3, 
                 slowd_period: int = 3) -> np.ndarray:
        """Stochastic Oscillator %K"""
        slowk, slowd = talib.STOCH(high.astype(np.float64), 
                                   low.astype(np.float64), 
                                   close.astype(np.float64), 
                                   fastk_period=fastk_period, 
                                   slowk_period=slowk_period, 
                                   slowd_period=slowd_period)
        return slowk
    
    def _stoch_d(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                 fastk_period: int = 14, slowk_period: int = 3, 
                 slowd_period: int = 3) -> np.ndarray:
        """Stochastic Oscillator %D"""
        slowk, slowd = talib.STOCH(high.astype(np.float64), 
                                   low.astype(np.float64), 
                                   close.astype(np.float64), 
                                   fastk_period=fastk_period, 
                                   slowk_period=slowk_period, 
                                   slowd_period=slowd_period)
        return slowd
    
    def _stochrsi(self, close: np.ndarray, period: int = 14) -> np.ndarray:
        """Stochastic RSI (returns %K)"""
        k, d = talib.STOCHRSI(close.astype(np.float64), timeperiod=period)
        return k
    
    def _stochrsi_k(self, close: np.ndarray, period: int = 14) -> np.ndarray:
        """Stochastic RSI %K"""
        k, d = talib.STOCHRSI(close.astype(np.float64), timeperiod=period)
        return k
    
    def _stochrsi_d(self, close: np.ndarray, period: int = 14) -> np.ndarray:
        """Stochastic RSI %D"""
        k, d = talib.STOCHRSI(close.astype(np.float64), timeperiod=period)
        return d
    
    def _adx(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
             period: int = 14) -> np.ndarray:
        """Average Directional Index"""
        return talib.ADX(high.astype(np.float64), 
                         low.astype(np.float64), 
                         close.astype(np.float64), 
                         timeperiod=period)
    
    def _dx(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
            period: int = 14) -> np.ndarray:
        """Directional Movement Index"""
        return talib.DX(high.astype(np.float64), 
                        low.astype(np.float64), 
                        close.astype(np.float64), 
                        timeperiod=period)
    
    def _minus_di(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                  period: int = 14) -> np.ndarray:
        """Minus Directional Indicator"""
        return talib.MINUS_DI(high.astype(np.float64), 
                              low.astype(np.float64), 
                              close.astype(np.float64), 
                              timeperiod=period)
    
    def _plus_di(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                 period: int = 14) -> np.ndarray:
        """Plus Directional Indicator"""
        return talib.PLUS_DI(high.astype(np.float64), 
                             low.astype(np.float64), 
                             close.astype(np.float64), 
                             timeperiod=period)
    
    def _minus_dm(self, high: np.ndarray, low: np.ndarray, period: int = 14) -> np.ndarray:
        """Minus Directional Movement"""
        return talib.MINUS_DM(high.astype(np.float64), 
                              low.astype(np.float64), 
                              timeperiod=period)
    
    def _plus_dm(self, high: np.ndarray, low: np.ndarray, period: int = 14) -> np.ndarray:
        """Plus Directional Movement"""
        return talib.PLUS_DM(high.astype(np.float64), 
                             low.astype(np.float64), 
                             timeperiod=period)
    
    def _cci(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
             period: int = 14) -> np.ndarray:
        """Commodity Channel Index"""
        return talib.CCI(high.astype(np.float64), 
                         low.astype(np.float64), 
                         close.astype(np.float64), 
                         timeperiod=period)
    
    def _mfi(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
              volume: np.ndarray, period: int = 14) -> np.ndarray:
        """Money Flow Index"""
        return talib.MFI(high.astype(np.float64), 
                         low.astype(np.float64), 
                         close.astype(np.float64), 
                         volume.astype(np.float64), 
                         timeperiod=period)
    
    def _willr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
               period: int = 14) -> np.ndarray:
        """Williams %R"""
        return talib.WILLR(high.astype(np.float64), 
                           low.astype(np.float64), 
                           close.astype(np.float64), 
                           timeperiod=period)
    
    def _sar(self, high: np.ndarray, low: np.ndarray, close: np.ndarray = None, acceleration: float = 0.02, maximum: float = 0.2) -> np.ndarray:
        """SAR (Parabolic SAR)"""
        return talib.SAR(high.astype(np.float64), 
                         low.astype(np.float64), 
                         acceleration=acceleration, 
                         maximum=maximum)
    
    def _atr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
             period: int = 14) -> np.ndarray:
        """Average True Range"""
        result = talib.ATR(high.astype(np.float64), 
                          low.astype(np.float64), 
                          close.astype(np.float64), 
                          timeperiod=period)
        # Ensure we return a numpy array, not a string
        if isinstance(result, str):
            raise ValueError(f"ATR function returned string: {result}")
        return result
    
    def _natr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
              period: int = 14) -> np.ndarray:
        """Normalized Average True Range"""
        return talib.NATR(high.astype(np.float64), 
                          low.astype(np.float64), 
                          close.astype(np.float64), 
                          timeperiod=period)
    
    def _trange(self, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
        """True Range"""
        return talib.TRANGE(high.astype(np.float64), 
                           low.astype(np.float64), 
                           close.astype(np.float64))
    
    def _obv(self, close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """On Balance Volume"""
        c = np.asarray(close, dtype=np.float64)
        v = np.asarray(volume, dtype=np.float64)
        result = talib.OBV(c, v)
        # Ensure we return a numpy array, not a string
        if isinstance(result, str):
            raise ValueError(f"OBV function returned string: {result}")
        return result
    
    def _mom(self, close: np.ndarray, period: int = 10) -> np.ndarray:
        """Momentum"""
        return talib.MOM(close.astype(np.float64), timeperiod=period)
    
    def _roc(self, close: np.ndarray, period: int = 10) -> np.ndarray:
        """Rate of Change"""
        return talib.ROC(close.astype(np.float64), timeperiod=period)
    
    def _cmo(self, close: np.ndarray, period: int = 14) -> np.ndarray:
        """Chande Momentum Oscillator"""
        return talib.CMO(close.astype(np.float64), timeperiod=period)
    
    def _ultosc(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                period1: int = 7, period2: int = 14, 
                period3: int = 28) -> np.ndarray:
        """Ultimate Oscillator"""
        return talib.ULTOSC(high.astype(np.float64), 
                           low.astype(np.float64), 
                           close.astype(np.float64), 
                           timeperiod1=period1, 
                           timeperiod2=period2, 
                           timeperiod3=period3)
    
    def _ppo(self, close: np.ndarray, fastperiod: int = 12, 
             slowperiod: int = 26) -> np.ndarray:
        """Percentage Price Oscillator"""
        return talib.PPO(close.astype(np.float64), 
                         fastperiod=fastperiod, 
                         slowperiod=slowperiod)
    
    def _stddev(self, close: np.ndarray, period: int = 5, nbdev: float = 1.0) -> np.ndarray:
        """Standard Deviation"""
        result = talib.STDDEV(close.astype(np.float64), timeperiod=period, nbdev=nbdev)
        # Ensure we return a numpy array, not a string
        if isinstance(result, str):
            raise ValueError(f"STDDEV function returned string: {result}")
        return result
    
    def _var(self, close: np.ndarray, period: int = 5, nbdev: float = 1.0) -> np.ndarray:
        """Variance"""
        return talib.VAR(close.astype(np.float64), timeperiod=period, nbdev=nbdev)
    
    def _linearreg(self, close: np.ndarray, period: int = 14) -> np.ndarray:
        """Linear Regression"""
        return talib.LINEARREG(close.astype(np.float64), timeperiod=period)
    
    def _cum(self, data: np.ndarray) -> np.ndarray:
        """Cumulative sum from the first available bar (vectorized)."""
        arr = np.asarray(data, dtype=np.float64)
        return np.cumsum(arr, dtype=np.float64)
    
    # --- GenMoM family (time-series approximations) ---
    def _rolling_monthly_returns(self, close: np.ndarray, days_per_month: int = 21) -> np.ndarray:
        """Approximate monthly returns from daily close using fixed days_per_month spacing."""
        c = np.asarray(close, dtype=np.float64)
        result = np.full(len(c), np.nan, dtype=np.float64)
        if len(c) <= days_per_month:
            return result
        prev = np.roll(c, days_per_month)
        ret = (c / prev) - 1.0
        ret[:days_per_month] = np.nan
        return ret
    
    def _genmom_generic(self, close: np.ndarray, months: int = 12, days_per_month: int = 21) -> np.ndarray:
        """Cumulative 12-month return including the most recent month (rolling)."""
        mr = self._rolling_monthly_returns(close, days_per_month)
        # build rolling product of last `months` monthly returns
        res = np.full(len(mr), np.nan, dtype=np.float64)
        for i in range(len(mr)):
            start = i - months * days_per_month
            if start < 0:
                continue
            # sample monthly returns every days_per_month step
            window = mr[start+days_per_month:i+1:days_per_month]
            if len(window) == months and not np.any(np.isnan(window)):
                res[i] = np.prod(1.0 + window) - 1.0
        return res
    
    def _genmom_fip(self, close: np.ndarray, months: int = 12, days_per_month: int = 21) -> np.ndarray:
        """Cumulative 12-month return excluding the most recent month (rolling)."""
        mr = self._rolling_monthly_returns(close, days_per_month)
        res = np.full(len(mr), np.nan, dtype=np.float64)
        for i in range(len(mr)):
            start = i - months * days_per_month
            if start < 0:
                continue
            window = mr[start+days_per_month:i+1:days_per_month]
            # exclude last month if available
            if len(window) == months and not np.any(np.isnan(window)):
                window_ex = window[:-1]
                res[i] = np.prod(1.0 + window_ex) - 1.0
        return res
    
    def _fip_score_ts(self, close: np.ndarray, lookback: int = 252, months: int = 12, days_per_month: int = 21) -> np.ndarray:
        """Daily FIP score approximation: sign(M_FIP) * (pct_negative - pct_positive) over last N days."""
        c = np.asarray(close, dtype=np.float64)
        daily_ret = np.full(len(c), np.nan, dtype=np.float64)
        daily_ret[1:] = c[1:] / c[:-1] - 1.0
        m_fip = self._genmom_fip(close, months=months, days_per_month=days_per_month)
        res = np.full(len(c), np.nan, dtype=np.float64)
        for i in range(len(c)):
            if i < lookback:
                continue
            window = daily_ret[i - lookback + 1:i + 1]
            if np.any(np.isnan(window)) or np.isnan(m_fip[i]):
                continue
            pos = np.mean(window > 0)
            neg = np.mean(window < 0)
            res[i] = np.sign(m_fip[i]) * (neg - pos)
        return res
    
    # Data access functions
    def _data_access(self, data: Dict[str, np.ndarray], field: str) -> np.ndarray:
        """Access data fields (open, high, low, close, volume)"""
        return data[field]
    
    # Aggregation functions
    def _min(self, data: np.ndarray, period: int = 1, exclude_current: bool = True) -> np.ndarray:
        """Get minimum value over the last n periods"""
        if period <= 1:
            return data
        
        # Ensure data is numeric
        if data.dtype.kind not in 'fc':
            try:
                data = np.asarray(data, dtype=np.float64)
            except (ValueError, TypeError):
                raise ValueError(f"min() function requires numeric data, got {data.dtype}")
        
        result = np.full_like(data, np.nan)
        offset = 1 if exclude_current else 0
        
        for i in range(period + offset - 1, len(data)):
            start_idx = i - period - offset + 1
            end_idx = i - offset + 1
            result[i] = np.min(data[start_idx:end_idx])
        
        return result
    
    def _max(self, data: np.ndarray, period: int = 1, exclude_current: bool = True) -> np.ndarray:
        """Get maximum value over the last n periods"""
        if period <= 1:
            return data
        
        # Ensure data is numeric
        if data.dtype.kind not in 'fc':
            try:
                data = np.asarray(data, dtype=np.float64)
            except (ValueError, TypeError):
                raise ValueError(f"max() function requires numeric data, got {data.dtype}")
        
        result = np.full_like(data, np.nan)
        offset = 1 if exclude_current else 0
        
        for i in range(period + offset - 1, len(data)):
            start_idx = i - period - offset + 1
            end_idx = i - offset + 1
            result[i] = np.max(data[start_idx:end_idx])
        
        return result
    
    def _count(self, data: np.ndarray, period: int = 1, exclude_current: bool = True) -> np.ndarray:
        """Count non-zero/non-nan values over the last n periods"""
        if period <= 1:
            return np.ones(len(data), dtype=np.float64)
        # normalize to numeric 0/1 for boolean inputs
        if data.dtype == bool:
            data = data.astype(np.int8)
        result = np.full(len(data), np.nan, dtype=np.float64)
        offset = 1 if exclude_current else 0
        
        for i in range(period + offset - 1, len(data)):
            start_idx = i - period - offset + 1
            end_idx = i - offset + 1
            window = data[start_idx:end_idx]
            result[i] = np.sum((~np.isnan(window)) & (window != 0)) if window.dtype.kind in 'fc' else np.sum(window != 0)
        
        return result
    
    def _countstreak(self, data: np.ndarray, condition: str = 'positive', 
                     period: int = 1, exclude_current: bool = True) -> np.ndarray:
        """Count consecutive streaks meeting a condition over the last n periods
        Accepts flexible signatures:
        - countstreak(boolean_series, period)
        - countstreak(series, 'positive'|'negative'|'above_zero'|'below_zero', period[, exclude_current])
        """
        # _count_consecutive_* below index windows positionally (data[i] for small i
        # counting from the window start), which silently breaks if data is a pandas
        # Series -- a sliced window retains the ORIGINAL labels (e.g. [37, 38, 39, ...]
        # not [0, 1, 2, ...]), so data[i] does a label lookup that KeyErrors for any
        # window not starting at the series' first row. Converting to a plain ndarray
        # up front makes all indexing below positional, as every caller already assumes.
        if not isinstance(data, np.ndarray):
            data = np.asarray(data)

        # Normalize arguments when called as countstreak(condition, N)
        if isinstance(condition, (int, float)) and (isinstance(period, bool) or period == 1):
            period = int(condition)
            # If data is boolean or numeric mask, use above_zero semantics
            if isinstance(data, np.ndarray) and data.dtype == bool:
                condition = 'above_zero'
                data = data.astype(np.int8)
            else:
                # Default to above_zero for numeric inputs
                condition = 'above_zero'
        
        if period <= 1:
            return np.ones(len(data), dtype=np.float64)
        # If boolean array is provided, 'positive' means True
        if isinstance(data, np.ndarray) and data.dtype == bool:
            cond = 'above_zero'
            data = data.astype(np.int8)
        else:
            cond = condition
        result = np.full(len(data), np.nan, dtype=np.float64)
        offset = 1 if exclude_current else 0
        
        for i in range(period + offset - 1, len(data)):
            start_idx = i - period - offset + 1
            end_idx = i - offset + 1
            window = data[start_idx:end_idx]
            if cond == 'positive':
                streak = self._count_consecutive_positive(window)
            elif cond == 'negative':
                streak = self._count_consecutive_negative(window)
            elif cond == 'above_zero':
                streak = self._count_consecutive_above(window, 0)
            elif cond == 'below_zero':
                streak = self._count_consecutive_below(window, 0)
            else:
                streak = 0
            result[i] = float(streak)
        
        return result
    
    def _abs(self, data: np.ndarray) -> np.ndarray:
        """Get absolute values"""
        # Ensure data is numeric
        if data.dtype.kind not in 'fc':
            try:
                data = np.asarray(data, dtype=np.float64)
            except (ValueError, TypeError):
                raise ValueError(f"abs() function requires numeric data, got {data.dtype}")
        
        return np.abs(data)
    
    def _ceil(self, data: np.ndarray) -> np.ndarray:
        """Ceiling function"""
        # Ensure data is numeric
        if data.dtype.kind not in 'fc':
            try:
                data = np.asarray(data, dtype=np.float64)
            except (ValueError, TypeError):
                raise ValueError(f"ceil() function requires numeric data, got {data.dtype}")
        
        return np.ceil(data)
    
    def _floor(self, data: np.ndarray) -> np.ndarray:
        """Floor function"""
        # Ensure data is numeric
        if data.dtype.kind not in 'fc':
            try:
                data = np.asarray(data, dtype=np.float64)
            except (ValueError, TypeError):
                raise ValueError(f"floor() function requires numeric data, got {data.dtype}")
        
        return np.floor(data)
    
    def _round(self, data: np.ndarray, decimals: int = 0) -> np.ndarray:
        """Round to specified decimal places"""
        # Ensure data is numeric
        if data.dtype.kind not in 'fc':
            try:
                data = np.asarray(data, dtype=np.float64)
            except (ValueError, TypeError):
                raise ValueError(f"round() function requires numeric data, got {data.dtype}")
        
        return np.round(data, decimals)
    
    def _square(self, data: np.ndarray) -> np.ndarray:
        """Square the values"""
        # Ensure data is numeric
        if data.dtype.kind not in 'fc':
            try:
                data = np.asarray(data, dtype=np.float64)
            except (ValueError, TypeError):
                raise ValueError(f"square() function requires numeric data, got {data.dtype}")
        
        return np.square(data)
    
    # Historical access functions (simplified versions for now)
    def _n_days_ago(self, data: np.ndarray, n: int, exclude_current: bool = True) -> np.ndarray:
        """Get data from n days ago"""
        if n >= len(data):
            return np.full(len(data), np.nan)
        
        offset = n + (1 if exclude_current else 0)
        result = np.full_like(data, np.nan)
        result[offset:] = data[:-offset]
        return result
    
    def _n_weeks_ago(self, data: np.ndarray, n: int, exclude_current: bool = True) -> np.ndarray:
        """Get data from n weeks ago (7*n days)"""
        return self._n_days_ago(data, n * 7, exclude_current)
    
    def _n_months_ago(self, data: np.ndarray, n: int, exclude_current: bool = True) -> np.ndarray:
        """Get data from n months ago (30*n days)"""
        return self._n_days_ago(data, n * 30, exclude_current)
    
    def _n_years_ago(self, data: np.ndarray, n: int, exclude_current: bool = True) -> np.ndarray:
        """Get data from n years ago (365*n days)"""
        return self._n_days_ago(data, n * 365, exclude_current)
    
    # Helper methods for streak counting
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
        # Timeframe function
        self.functions['tf'] = self._tf
        
        # Crossover function (for explicit crossover calls)
        self.functions['crossover'] = self._crossover

    def _tf(self, condition: np.ndarray, timeframe: str) -> np.ndarray:
        """Apply timeframe filtering by OR-reducing inside calendar buckets and broadcasting back as a daily mask."""
        if condition is None:
            return condition
        cond = np.asarray(condition).astype(bool)
        # Normalize timeframe string
        tf = str(timeframe).lower().strip("'\"")
        tf = {'d':'daily','w':'weekly','m':'monthly','y':'yearly'}.get(tf, tf)
        if tf == 'daily':
            return cond
        if self._current_dates is None or len(self._current_dates) != len(cond):
            # Without dates, safest is pass-through
            return cond
        dates = self._current_dates
        # Choose bucket id per day
        if tf == 'weekly':
            bucket_ids = dates.astype('datetime64[W]')
        elif tf == 'monthly':
            bucket_ids = dates.astype('datetime64[M]')
        elif tf == 'yearly':
            bucket_ids = dates.astype('datetime64[Y]')
        else:
            return cond
        key = (bucket_ids.dtype.str, bucket_ids[0].astype('datetime64[D]').astype(int), bucket_ids[-1].astype('datetime64[D]').astype(int), tf, len(bucket_ids))
        spans = self._bucket_cache.get(key)
        if spans is None:
            # Compute contiguous spans where bucket id is constant
            ids = bucket_ids.astype('int64')
            # Boundaries where id changes
            change = np.empty(len(ids), dtype=bool)
            change[0] = True
            change[1:] = ids[1:] != ids[:-1]
            starts = np.nonzero(change)[0]
            ends = np.concatenate((starts[1:] - 1, np.array([len(ids) - 1])))
            spans = np.stack([starts, ends], axis=1)
            self._bucket_cache[key] = spans
        out = np.zeros_like(cond, dtype=bool)
        # OR within each span, broadcast
        for s, e in spans:
            if np.any(cond[s:e+1]):
                out[s:e+1] = True
        return out
    
    def _crossover(self, series1: np.ndarray, series2: np.ndarray) -> np.ndarray:
        """
        Crossover function - detects when series1 crosses over series2
        
        Args:
            series1: First series (usually a technical indicator)
            series2: Second series (usually a threshold or another indicator)
        
        Returns:
            Boolean array where True indicates crossover occurred
        """
        if len(series1) != len(series2):
            raise ValueError("Series must have the same length for crossover detection")
        
        # Create crossover signals
        crossover = np.zeros(len(series1), dtype=bool)
        
        for i in range(1, len(series1)):
            # Crossover occurs when series1 was below series2 at i-1 and above at i
            if (series1[i-1] <= series2[i-1]) and (series1[i] > series2[i]):
                crossover[i] = True
        
        return crossover

