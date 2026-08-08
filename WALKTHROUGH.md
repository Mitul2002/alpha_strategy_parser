# How to talk about this project

Companion notes for the interview — what's real, what I fixed, and what's still known-broken.

## The 30-second version

`alpha_strategy_parser` is a grammar-based strategy engine: a strategy string like
`ema(close, 50) > ema(close, 200) AND rsi(close, 14) > 40` gets parsed and evaluated
against OHLCV data for an arbitrary universe of stocks, via a 40+-function indicator
registry (RSI, MACD, Bollinger, Stochastic, ADX, OBV, CCI, Williams %R, SAR, a
`crossover` operator, generic lag access via `n_days_ago`, multi-timeframe via `tf()`),
with a FastAPI backend and a Vue frontend. When I actually tried to run it end-to-end
against its real ~2,050-symbol dataset, I found and fixed: two Python syntax errors
that blocked the backend from importing at all, a missing data-path wiring, a Windows
node_modules platform mismatch, and — the interesting one — a confirmed, verified bug
where the advertised multi-timeframe feature (`tf(condition, 'weekly')`) silently did
nothing, for two independent reasons stacked on top of each other.

## What was actually broken, and how I found each one

**1. Backend wouldn't import at all.** Two syntax errors in `webapi/app.py`
(over-indented `continue` statements inside `try` blocks) — this wasn't a subtle bug,
it's a plain `IndentationError`, meaning the backend had not been successfully started
in whatever state the repo was last left in. Found by just trying to import it.

**2. The real dataset wasn't wired up.** `/symbols` and `/ohlcv` default to a
`DATA_PARTITIONED_PATH` that pointed at a folder that doesn't exist on this machine.
The actual ~2,050-symbol parquet dataset (matching the resume's "2,000+ NSE stocks"
figure almost exactly) was sitting in a sibling project folder
(`rsi_forward_returns/data_partitioned`) in exactly the flat-file-per-symbol format
the backend expects — just needed the env var pointed at it.

**3. Frontend node_modules were built for Linux, this machine is Windows.** Vite's
`esbuild` dependency ships a platform-specific compiled binary. Fix: fresh
`npm install` under a Windows-native Node (installed via conda-forge, since none was
present on the system at all).

**4. Multi-timeframe (`tf()`) was completely non-functional — confirmed, not assumed.**
Tested it empirically before touching any code: ran the identical condition through
`tf(cond, 'daily')`, `tf(cond, 'weekly')`, `tf(cond, 'monthly')` and got **the exact
same signal count for all three** (431,149). That's the tell — a real bug produces
wrong-but-plausible numbers; this produced *identical* numbers, which only happens if
the timeframe argument is being silently ignored. Traced it to two independent causes:
  - `FunctionRegistry.set_context()` only ever looked for a `'date'` column. The real
    production parquet data's column is named `'datetime'`. So the date context needed
    for bucketing was silently `None`.
  - Even with dates available, `StrategyExecutor._execute_multi_timeframe_condition()`
    never actually called the bucketing logic — it had a literal
    `# TODO: Implement actual timeframe resampling logic` comment and just returned
    the daily condition unchanged, regardless of what timeframe was requested. The
    bucketing math itself (`FunctionRegistry._tf()`, OR-reduce within a calendar
    bucket, broadcast back to a daily mask) was already correctly implemented and
    registered — it just was never wired up to the multi-timeframe execution path.
  
  Fixed both. Verified after the fix: daily=431,149, weekly=803,344 (~1.9x),
  monthly=1,837,878 (~4.3x) — sensible, monotonically increasing, exactly the shape
  you'd expect from "OR-reduce and broadcast within larger buckets."

## What's genuinely general now (verified, not assumed)

Built `strategy_library_engine.py` in the *other* project (`nse_numba_backtester`) to
prove the two systems compose: it swaps that engine's hardcoded RSI-cross entry signal
for a call into this project's parser, feeding the result into the unmodified
Numba-JIT execution loop. Verified on the full 2,050-symbol universe with two
structurally different strategies (EMA-trend+RSI, and MACD-crossover+ATR) — both
clean, 0 errors. See that project's README for the numbers.

## Known limitations — say these before they're asked

- **Not exhaustively tested.** Verified a representative sample of the 40+ registered
  functions in different combinations, not every possible pairing.
- **The `tf()` fix hasn't been proven against a hand-computed ground truth**, only
  against "does the count change sensibly in the expected direction." Good enough to
  say "multi-timeframe now works," not good enough to claim numerically verified
  bucket boundaries without more work.
- **`executeStrategyFullScale` in `backendService.js` calls a `/execute-full-scale`
  route that doesn't exist on the backend** — but it's dead code, nothing in the UI
  calls it (`NewStrategy.vue` only calls `executeStrategyMultiLookahead`, which works).
  Worth deleting, not worth panicking about.
- **The repo has a lot of dead weight** — `app_broken.py`, `app_broken_again.py`,
  multiple `.backup`/`.broken`/`.debug` file variants in both `webapi/` and
  `alpha-strategy-frontend/src/`. Not cleaned up yet. If demoing the raw repo, be ready
  to explain that `app.py` and `App.vue` are the live files, the rest is history.
