# alpha_strategy_parser

A grammar-based strategy engine for NSE equities. Write a strategy as a
plain string —

```
ema(close, 50) > ema(close, 200) AND rsi(close, 14) > 40
```

— and it gets parsed, evaluated against OHLCV data for an arbitrary
symbol universe through a 40+-function technical indicator registry
(RSI, MACD, Bollinger Bands, Stochastic, ADX, OBV, CCI, Williams %R,
SAR, a `crossover` operator, generic lag access via `n_days_ago`,
multi-timeframe resampling via `tf()`), and served through a FastAPI
backend with a Vue 3 frontend.

The full ~2,050-symbol NSE dataset is bundled directly into the Docker
image — clone, run one command, and it works against real market data
with no external dependency.

## Quick start

```bash
docker compose up --build -d
```

- Frontend: **http://localhost:5173**
- Backend API: **http://localhost:8000** (`/health`, `/symbols`, `/ohlcv/{symbol}`)

First build takes ~1-2 minutes (TA-Lib's compiled dependency via
conda-forge). See [`DEPLOYMENT.md`](./DEPLOYMENT.md) for the full
walkthrough, including a live-tunnel option if you'd rather demo it
running on your own machine in real time instead of handing someone
the repo.

## Architecture

```
strategy string
      |
      v
 ANTLR4-style grammar (grammar/Strategy.g4)   <- formal parser, not eval()/regex
      |  parse tree
      v
 src/simple_parser.py                          <- walks the parse tree
      |  calls into
      v
 src/function_registry.py                      <- 40+ indicator functions (TA-Lib-backed)
      |
      v
 src/strategy_executor.py                      <- evaluates comparisons/AND/OR,
      |                                           produces boolean signal arrays
      v
 webapi/app.py (FastAPI)                        <- /symbols, /ohlcv, /execute-strategy...
      |
      v
 alpha-strategy-frontend (Vue 3 + Vite + Tailwind + lightweight-charts)
```

A formal grammar rather than `eval()`/string-hacking buys two things:
no arbitrary-code-execution surface on user-supplied strategy strings,
and unambiguous operator precedence (`AND`/`OR`, parenthesization,
nested function calls like `sma(atr(high, low, close, 14), 20)`,
attribute access like `bbands(close, 20, 2).upper`) — a real parse tree
instead of regex spaghetti.

## Composes with a Numba-JIT execution engine

[`nse_numba_backtester`](https://github.com/Mitul2002/nse_numba_backtester)
is a separate project — a vectorized, Numba-JIT backtesting engine
(~25x faster than a vectorbt baseline on the full universe). Its
`strategy_library_engine.py` swaps that engine's hardcoded entry-signal
logic for a call into this project's parser, so a strategy string
written here can drive backtests there without touching the execution
loop. Verified on the full 2,050-symbol universe across 50+ diverse
strategies, cross-validated against vectorbt (95.3% mean exact
trade-count match, 0.991 mean Sharpe correlation).

**Parser here → signal generation. Numba engine there → execution at
scale.** Deliberately separate concerns, composed through one adapter.

## What's real here — and what isn't yet

See [`WALKTHROUGH.md`](./WALKTHROUGH.md) for the full story: four real
bugs found and fixed while getting this running end-to-end (including a
subtle one — multi-timeframe resampling silently returning identical
signal counts across daily/weekly/monthly, traced to two independent
causes), what's verified vs. what isn't, and known limitations stated
plainly rather than glossed over.

## Repo layout

```
grammar/        ANTLR4 grammar definition
src/            parser, function registry, strategy executor
webapi/         FastAPI backend
alpha-strategy-frontend/   Vue 3 frontend
market_data/    full ~2,050-symbol NSE dataset (bundled, used by default)
demo_data/      lightweight 6-symbol fallback (scripts/build_demo_data.py regenerates it)
examples/       sample strategy strings, mock server for frontend-only dev
```
