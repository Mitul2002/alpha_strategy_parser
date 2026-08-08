// Mock data for frontend testing
export const mockFullScaleData = {
  "ok": true,
  "results": {
    "strategy": "ema(close, 50) > ema(close, 200)",
    "aggregated_metrics": {
      "overall": {
        "avg_return": 0.0008,
        "win_rate": 0.4647,
        "sharpe_ratio": 0.073,
        "sortino_ratio": 0.310,
        "information_ratio": 0.126,
        "max_runup": 0.1975,
        "avg_std_dev": 0.0310,
        "max_drawdown": -0.5935,
        "best_return": 4.2298,
        "worst_return": -0.9876,
        "total_return": 3847.9211,
        "total_signals": 3288168
      },
      "1": {
        "avg_return": 0.0008,
        "win_rate": 0.4647,
        "sharpe_ratio": 0.073,
        "sortino_ratio": 0.310,
        "information_ratio": 0.126,
        "max_runup": 0.1975,
        "avg_std_dev": 0.0310,
        "max_drawdown": -0.5935,
        "best_return": 4.2298,
        "worst_return": -0.9876,
        "total_return": 3847.9211,
        "total_signals": 3288168
      },
      "5": {
        "avg_return": 0.0045,
        "win_rate": 0.4766,
        "sharpe_ratio": 0.815,
        "sortino_ratio": 0.650,
        "information_ratio": 0.450,
        "max_runup": 0.2500,
        "avg_std_dev": 0.0350,
        "max_drawdown": -0.4500,
        "best_return": 2.5000,
        "worst_return": -0.8000,
        "total_return": 4500.0000,
        "total_signals": 3288165
      },
      "10": {
        "avg_return": 0.0095,
        "win_rate": 0.4839,
        "sharpe_ratio": 1.103,
        "sortino_ratio": 0.900,
        "information_ratio": 0.750,
        "max_runup": 0.3200,
        "avg_std_dev": 0.0400,
        "max_drawdown": -0.3500,
        "best_return": 3.2000,
        "worst_return": -0.7000,
        "total_return": 9500.0000,
        "total_signals": 3288148
      },
      "20": {
        "avg_return": 0.0199,
        "win_rate": 0.4960,
        "sharpe_ratio": 1.589,
        "sortino_ratio": 1.200,
        "information_ratio": 1.100,
        "max_runup": 0.4500,
        "avg_std_dev": 0.0500,
        "max_drawdown": -0.2500,
        "best_return": 4.5000,
        "worst_return": -0.6000,
        "total_return": 19900.0000,
        "total_signals": 3288059
      }
    },
    "stockwise_metrics": [
      {
        "symbol": "NCC",
        "total_signals": 4007,
        "total_return": 9.493492,
        "avg_return": 0.0024,
        "win_rate": 0.487896,
        "sharpe_ratio": 1.033161,
        "sortino_ratio": 1.200000,
        "information_ratio": 0.850000,
        "max_runup": 0.150000,
        "max_drawdown": -0.120000,
        "best_return": 0.150000,
        "worst_return": -0.120000
      },
      {
        "symbol": "GMBREW",
        "total_signals": 3201,
        "total_return": 9.308529,
        "avg_return": 0.0029,
        "win_rate": 0.465167,
        "sharpe_ratio": 0.797301,
        "sortino_ratio": 0.950000,
        "information_ratio": 0.700000,
        "max_runup": 0.180000,
        "max_drawdown": -0.150000,
        "best_return": 0.180000,
        "worst_return": -0.150000
      },
      {
        "symbol": "GABRIEL",
        "total_signals": 3379,
        "total_return": 8.950807,
        "avg_return": 0.0026,
        "win_rate": 0.468620,
        "sharpe_ratio": 0.520880,
        "sortino_ratio": 0.650000,
        "information_ratio": 0.450000,
        "max_runup": 0.120000,
        "max_drawdown": -0.180000,
        "best_return": 0.120000,
        "worst_return": -0.180000
      },
      {
        "symbol": "AEGISLOG",
        "total_signals": 3674,
        "total_return": 8.600273,
        "avg_return": 0.0023,
        "win_rate": 0.474272,
        "sharpe_ratio": 0.955614,
        "sortino_ratio": 1.100000,
        "information_ratio": 0.800000,
        "max_runup": 0.140000,
        "max_drawdown": -0.130000,
        "best_return": 0.140000,
        "worst_return": -0.130000
      },
      {
        "symbol": "BAJFINANCE",
        "total_signals": 5058,
        "total_return": 7.779508,
        "avg_return": 0.0015,
        "win_rate": 0.500494,
        "sharpe_ratio": 0.889520,
        "sortino_ratio": 1.050000,
        "information_ratio": 0.750000,
        "max_runup": 0.110000,
        "max_drawdown": -0.100000,
        "best_return": 0.110000,
        "worst_return": -0.100000
      }
    ],
    "performance_stats": {
      "symbols_per_second": 82,
      "signals_per_second": 132303,
      "total_symbols": 2050,
      "success_rate": 100.0
    }
  }
};
