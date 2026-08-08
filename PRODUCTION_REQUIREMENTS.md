# Alpha Strategy Engine - Production Requirements

## 1) Objective
- Build a local, production-grade engine that executes strategies mixing TA-Lib, Ehlers, and custom indicators over 15 years of daily OHLCV for ~2,000 symbols.
- End-to-end run time: ≤10s (target 5s) on consumer laptops:
  - HP Pavilion x360 i7-10th Gen, 16GB RAM, 1TB SSD (Windows 10)
  - Apple M2 Max, 32GB RAM (macOS)
- Accuracy: ≥95% numerical parity vs baselines (TA-Lib reference and TradingView Pine where applicable).
- Robust local logging for ML/RL training datasets.

## 2) Scope
- Supported indicators/functions:
  - TA-Lib indicators in current app (keep coverage).
  - Ehlers indicators used by the app (SuperSmoother, RoofingFilter, FisherTransform, InstantaneousTrendline, BandPassFilter, etc.).
  - Custom functions: count, countstreak, historical accessors (n_days/weeks/months/years_ago), tf(condition, timeframe), crossover, arithmetic/property comparisons.
- Parser:
  - Maintain current parser; harden and cache parses. Optional ANTLR migration after performance targets met.
- Data:
  - Input: Parquet per symbol, columns: date/datetime, open, high, low, close, volume.
  - Output: Aggregated KPIs, per-symbol metrics, optional per-signal trades → Parquet. Append-only JSONL run index + DuckDB table.

## 3) Performance Targets (Acceptance)
- Full-universe run (2,000 symbols × ~3,800-4,000 rows) ≤10s; stretch ≤5s; max 4 workers.
- Memory stable (no unbounded copies); only required columns loaded.
- Accuracy ≥95% vs TA-Lib/TradingView Pine for mapped indicators.
- All tests pass: unit, property, integration, performance. Deterministic outputs where applicable.

## 4) Architecture & Stack
- Storage & data processing: Polars + Apache Arrow + Parquet; DuckDB for local analytics.
- Compute:
  - Prefer Polars expressions for common rolling/window indicators (SMA/EMA/STD/RSI/BB width/ATR eqv. if feasible).
  - Use NumPy + Numba for custom/Ehlers and boolean reductions; keep TA-Lib where it’s fastest/validated.
  - Fallback to Cython only if Numba insufficient for specific filters.
- Parallelism: Python multiprocessing (≤4 workers). Partition by symbol/time-chunk; shared-nothing workers.
- Service layer: FastAPI as thin control plane; background multiprocess queue for long jobs.
- Results & API:
  - Return summaries + top-N rows in JSON; persist full details to Parquet; provide artifact paths and pagination endpoints.
- Frontend: Keep current Vue app; pagination + progress UI; no heavy changes required.

## 5) Bottlenecks & Remedies (to implement)
- Function re-computation and parameter resolution overhead:
  - Add per-execution memoization keyed by node signature (subtree hash) to cache series.
  - Hoist common subexpressions from the parsed tree; evaluate once, reuse.
- Memory churn/copies (large arrays):
  - Replace np.roll with slice-based prev/cur comparisons; avoid np.pad; preallocate and reuse buffers.
  - Eliminate redundant np.asarray conversions; enforce contiguous float64 arrays at boundaries.
- count/countstreak boolean aggregations:
  - Implement as Numba-accelerated kernels (tight scans over boolean arrays). Keep dtypes stable.
- TA-Lib ↔ Polars boundary:
  - Use Polars expressions where feasible to avoid Python overhead; for TA-Lib/Ehlers, run in workers and reuse process-local buffers.
- API hot path using pandas:
  - Switch to Polars scan_parquet with column projection and lazy collect; move heavy execution off-request.
- Large JSON payloads:
  - Return aggregated KPIs + top-N; persist full stockwise/trades to Parquet; provide file links and pagination.
- Single-process CPU-bound API:
  - Keep API thin; run compute in worker pool (multiprocessing up to 4 workers).
- Parser scale/resilience:
  - Add parsed AST cache (strategy hash → AST). Consider ANTLR migration post-v1.
- History/logging throughput:
  - Keep JSONL index minimal; bulk write details to Parquet; maintain DuckDB ingestion CLI.

## 6) Prioritized Implementation Order (with complexity)

### Phase 1 — Quick Wins (week 1-2)
- Replace np.roll/pad with slices + preallocation  [Low]
- Vectorized forward-returns via shifts/-k  [Low]
- Memoize repeated indicators per request  [Low-Medium]
- AST cache (strategy → parsed tree)  [Low]
- Switch API reads to Polars scan_parquet + column projection  [Low]
- Limit response size + pagination + artifact links  [Low]
- Persist results to Parquet; DuckDB helper queries  [Low-Medium]

### Phase 2 — Indicator/Kernel Speedups (week 3-4)
- Faster count/countstreak via Numba  [Medium]
- Numba kernels for core Ehlers (SuperSmoother, RoofingFilter, FisherTransform)  [High for breadth, Medium per kernel]
- Keep more indicators in Polars expressions (SMA/EMA/STD/RSI/BB width) with parity checks  [Medium-High]

### Phase 3 — Execution Planner & Parallelism (week 5)
- Plan builder: DAG of unique subexpressions; topo-sort; shared buffer map  [Medium]
- Parallelism over symbols/chunks with multiprocessing (≤4 workers)  [Medium]
- Batch TA-Lib in workers with pinned buffers  [Medium]

### Phase 4 — API Job Model & UX (week 6)
- Move heavy compute to worker pool; API enqueues jobs; job status/polling endpoints  [Medium]
- Full result streaming or polling-based progress  [Medium]
- Trade extraction as paginated endpoint  [Low]

### Phase 5 — Hardening & Tests (week 7+)
- Migrate parser to ANTLR grammar (optional, post-SLA)  [High]
- End-to-end stabilization, regression/perf suite, profiling and tuning  [Medium]

## 7) Detailed Acceptance Tests
- Performance
  - Full-universe benchmark script runs ≤10s (target 5s) on both target machines with ≤4 workers.
  - Report includes phase timings (I/O, parse, plan, compute, aggregation, serialization).
- Accuracy
  - Indicator parity tests: TA-Lib vs engine for SMA/EMA/RSI/MACD/BB/ATR where mapped; tolerance: MAE≤5% of range or ≤1e-6 absolute where applicable.
  - Ehlers parity: compare against reference vectors (golden files) per indicator; tolerance agreed per indicator behavior.
  - TradingView Pine parity for mapped indicators and sample composite strategies; ≥95% matches on signals across dataset.
- Correctness
  - Crossover tests: detect rising cross and absence where not expected; tests at edges (first/last rows).
  - Arithmetic/property comparisons (bbands.upper/lower/middle; macd.signal/hist/macd) validated with fixtures.
  - Multi-lookahead: signals computed once; forward returns computed via shifts; cross-check counts and averages.
- Robustness
  - Large-run stress: simulate 2,500 symbols; ensure memory headroom; no crashes.
  - Fault injection: malformed strategy, missing columns, NaNs; assert graceful errors.
- Logging/Artifacts
  - JSONL index contains run_id, ts, strategy hash, hardware snapshot, kpis, artifact paths.
  - Parquet details readable; DuckDB `runs` table populated; example queries succeed.

## 8) Deliverables
- Optimized engine modules (executor, planner, indicator kernels), with docstrings and type hints.
- Worker manager (multiprocessing), config (workers≤4), and API endpoints: submit, status, summary, artifacts, list runs.
- Benchmark CLI and accuracy validator CLI.
- Parquet artifact schema and DuckDB ingestion helper.
- Documentation: setup, architecture notes, performance guide, testing guide.

## 9) Development Guidelines
- Use float64 contiguous arrays at module boundaries.
- Avoid full-array copies; reuse buffers; prefer slice ops.
- Guard against divide-by-zero, NaNs; define clear fill policy.
- Deterministic seeds for any stochastic components.
- Profile with py-spy/perf/cProfile; track CPU%, wall time, allocations.

## 10) Risks & Mitigations
- Ehlers numerical differences → maintain golden vectors and tolerances; document constants/initial conditions.
- Hardware variance → provide config presets (workers, chunk sizes); auto-detect cores/RAM.
- Parser complexity → keep AST cache; defer ANTLR until after SLA met.

## 11) Nice-to-Have (post v1 SLA)
- ANTLR parser migration.
- Rust (PyO3) implementations for the heaviest recursive filters.
- Streaming progress (SSE/WebSocket); UI charts for top signals.

## 12) Handoff Notes
- Code base locations:
  - Core engine: `alpha_strategy_parser/src/`
  - API: `alpha_strategy_parser/webapi/app.py`
  - Frontend: `alpha_strategy_parser/alpha-strategy-frontend/`
  - History: `alpha_strategy_parser/history/` (JSONL, Parquet, DuckDB)
- Start with Phase 1 items in order; run the performance benchmark after each step to track regressions. 