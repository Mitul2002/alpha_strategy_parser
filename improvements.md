I’ve reviewed the code and docs. Below are specific bottlenecks (beyond the Ehlers vs TA-Lib mismatch), concrete remedies, and an ideal stack with rationale.

### Bottlenecks (besides Ehlers Python/loop-heavy implementations)
- Function re-computation and parameter resolution overhead
  - Repeated nested function execution (e.g., same `ema(close, 50)` on both sides) is recomputed without memoization in `StrategyExecutor._execute_function_call`.
  - Generic `_resolve_operand_node` and arithmetic paths allocate and convert frequently, including nested dict evaluation.
  - Fix:
    - Add per-execution memoization keyed by node-id/serialized subtree to cache series results.
    - Pre-resolve and hoist common subexpressions from the parsed tree before execution.
- Memory churn and copying on 30M rows
  - `np.roll` in crossovers copies large arrays; arithmetic comparisons pad arrays with `np.pad`; many coercions to `np.asarray`.
  - Fix:
    - Use slice-based prev/cur comparisons: compute on `arr[1:]` vs `arr[:-1]`, then prepend a single False; avoid `np.roll`.
    - Replace `np.pad` with length-aligned views and scalar broadcasting; avoid full-length padding copies.
    - Prefer in-place masked operations where possible; reuse preallocated output arrays.
- Count/countstreak and boolean aggregations
  - Current implementation handles many shapes and conversions; for long windows this can degrade.
  - Fix:
    - Implement `count`/`countstreak` as Numba-accelerated scans over boolean arrays; keep types stable and avoid dtype switches.
- TA-Lib and Polars boundary
  - For full-universe runs, `high_performance_backend.py` reads with Polars but hands off to NumPy/TA-Lib, forcing materialization and Python boundary per indicator per symbol.
  - Fix:
    - Where feasible, implement high-usage indicators as Polars expressions (rolling mean/std, RSI, EMA variants) to keep compute in Rust and avoid Python overhead.
    - For indicators kept in TA-Lib, batch symbols and run in parallel workers with pinned process-local buffers to amortize overhead.
- Pandas in API hot path
  - `webapi/app.py` uses `pd.read_parquet` for `/execute-multi-lookahead`, which yields higher memory and Python overhead vs Polars’ lazy scan; the endpoint iterates every symbol synchronously in-process.
  - Fix:
    - Use Polars `scan_parquet` + `collect` lazily only for the columns required by the parsed strategy; avoid loading entire tables.
    - Move execution off-request into a job worker; return job id, stream incremental summaries.
- JSON payload size and serialization cost
  - Converting large arrays to JSON (trades, stockwise rows across 2,050+ symbols) is expensive and unnecessary for most UI views.
  - Fix:
    - Return only aggregated KPIs and a capped top-N stock list; persist full results to Parquet and reference via artifact URLs.
- Single-process CPU-bound API
  - Heavy CPU work inside FastAPI worker blocks event loop and limits throughput.
  - Fix:
    - Split the compute engine into a separate service (Rust/Python worker pool) behind a queue; scale workers independently.
- Parser scale and resilience
  - Regex-based parser is reasonable per request, but nested patterns and backtracking can degrade with pathological inputs.
  - Fix:
    - Keep for now; add a compiled AST cache (strategy hash → parsed AST).
    - Long-term: migrate to the existing ANTLR grammar (`grammar/Strategy.g4`) for linear-time parsing and richer validation.
- History and logging throughput
  - Writing large JSON logs per run can become a bottleneck.
  - Fix:
    - Continue the Parquet + DuckDB compaction flow; write only small JSONL indexes per run and bulk data to Parquet.

### Ehlers indicators: targeted fixes
- Port hot Ehlers implementations to Numba (nopython, parallel where applicable), operate on `float64` contiguous arrays; avoid Python loops/objects.
- If formulas require recursive filters, implement as fused kernels in Cython or Rust (PyO3) for zero-overhead loops and in-place buffers.
- Normalize interfaces to match TA-Lib: accept/return contiguous `np.ndarray[float64]`; avoid per-call class allocations (cache instances already started in `FunctionRegistry`).

### Execution at 30M+ rows: concrete plan
- Columnar pipeline
  - Keep data in Parquet (Arrow); use Polars lazy scans, project only needed columns, and predicate-pushdown with date filters.
- Strategy execution
  - Build a “plan” from the parsed AST:
    - Identify unique subexpressions; topologically sort; allocate output buffers once.
    - Evaluate each subexpression across the dataset with vectorized NumPy or Polars expressions (prefer Polars when equivalent is available).
  - Parallelism
    - Partition by symbol/time-chunk; process in a Ray/Dask pool or multiprocessing with shared memory; pin TA-Lib/Numba cores.
- Forward returns
  - Compute signals once; compute forward-returns with vectorized shifted arrays or Polars `shift(-k)`; aggregate reduction-only stats per lookahead in a single pass per k.

### Ideal tech stack and why
- Storage and data frame
  - Polars + Apache Arrow + Parquet
    - Why: Rust engine, SIMD, zero-copy Arrow, lazy execution, out-of-core capability; ideal for 30M+ rows and columnar ops.
- Compute/engine
  - Two-path strategy:
    - Path A (preferred): Polars expressions for rolling/window functions (EMA/SMA/STD/ATR approximations, RSI, BB width) to keep compute in Rust.
    - Path B: Numpy + Numba/Cython for custom/Ehlers where Polars lacks equivalents; TA-Lib for legacy indicators if it outperforms Numba.
    - Why: Polars minimizes Python overhead; Numba covers custom filters with JIT speed; TA-Lib remains a validated baseline.
- Orchestration/parallelism
  - Ray or multiprocessing + shared memory (or Polars built-in parallelism) for per-symbol partitions.
    - Why: Simple horizontal scaling over thousands of symbols; shared memory avoids serialization.
- Services
  - Backend API: FastAPI (thin control plane) + Uvicorn multiple workers
    - Why: Simple, well-supported; decouple control from compute.
  - Compute service: separate worker pool (Python + Numba or Rust microservice via PyO3/gRPC)
    - Why: Prevent API blocking; independent scaling and resource isolation.
- Artifacts/analytics
  - Results persisted to Parquet; DuckDB for interactive analytics; minimal JSON over wire.
    - Why: Columnar analytics at scale; low-latency small queries.
- Frontend
  - Vue 3 + Vite + CodeMirror 6 + current autocomplete system
    - Why: Already implemented and effective; keep UI thin and responsive.

### Specific remedies to apply in this codebase
- Add per-execution memoization in `StrategyExecutor` for function calls keyed by node signature; hoist common subexpressions once.
- Replace `np.roll` with slice comparisons; eliminate `np.pad` in arithmetic; preallocate output arrays and reuse buffers.
- Implement Numba kernels for:
  - Ehlers filters (core set first: SuperSmoother, RoofingFilter, FisherTransform).
  - `count`/`countstreak` and rolling boolean reductions.
- Introduce a “plan builder”:
  - Given the parsed AST, build a DAG of unique nodes; evaluate in topological order; store arrays in a dict of buffers.
- Move API compute to a worker:
  - Queue job (Redis/Celery or Ray Serve); return job id; stream progress; persist Parquet outputs; return aggregated KPIs and artifact links.
- Use Polars end-to-end in API paths:
  - Replace `pd.read_parquet` with `pl.scan_parquet` and project only required columns; collect just-in-time.
- Limit response size:
  - Aggregate KPIs + top-N stock rows; paginate stockwise results; keep trades behind a separate paginated endpoint.

If you want, I can draft the memoization and crossover slice edits, and sketch a Numba version of 1–2 Ehlers filters next.