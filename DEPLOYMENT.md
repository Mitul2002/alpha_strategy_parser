# Deploying / demoing this project

Two ways to let an interviewer actually run this themselves, both tested
end-to-end on 2026-08-18.

## Option A — Docker Compose (recommended: send them the repo, they run it)

**What you get**: a fully self-contained stack — backend (FastAPI +
TA-Lib) and frontend (Vue, built and served via nginx) — with the **real
~2,050-symbol NSE dataset bundled directly into the image** (`market_data/`,
351MB, copied from the same partitioned-parquet dataset the live app
uses). The interviewer needs nothing but Docker installed — no API keys,
no external data, no network access to your machine.

```bash
docker compose up --build -d
```

First build takes ~1-2 minutes (installs the conda env, mostly for
TA-Lib's compiled dependency; the 351MB data layer copies in a few
seconds). Then:

- Frontend: **http://localhost:5173**
- Backend API: **http://localhost:8000** (try `http://localhost:8000/health`
  and `http://localhost:8000/symbols` directly)

Verified working end-to-end: `POST /execute-multi-lookahead` with a real
strategy string against the full dataset returns aggregated metrics
across **2,050 symbols** and **2.8M+ signals** in one call — this is the
actual resume claim ("2,000+ NSE stocks"), not a placeholder.

To stop: `docker compose down`. To rebuild after a code change:
`docker compose up --build -d` again (Docker caches unchanged layers, so
this is fast after the first build).

**Why this is the better default for "let the interviewer try it
themselves"**: it's a one-command, fully offline, deterministic
artifact — no dependency on your PC being online, no tunnel URL that
might get flagged by a corporate firewall, no "works on my machine"
risk. Send them the repo (zip, or `git clone` if you push it somewhere
they can reach), they run one command.

## Option B — Local + tunnel (live demo during the call, your PC stays on)

If you'd rather demo it live yourself (e.g. walk through it on a call and
let them type a strategy string in real time against your machine):

1. Run the backend locally (not in Docker) so it uses your existing
   Python environment directly:
   ```bash
   uvicorn webapi.app:app --app-dir . --host 0.0.0.0 --port 8000
   ```
   (or just run `python webapi/app.py`, which does the same on
   `127.0.0.1:8000`)
2. Run the frontend dev server: `cd alpha-strategy-frontend && npm run dev`
3. Expose port 8000 (and 5173 if you want them to load the actual UI, not
   just hit the API) via a tunnel — **Cloudflare Tunnel** (`cloudflared
   tunnel --url http://localhost:8000`) or **ngrok** (`ngrok http 8000`)
   are the two standard options; Cloudflare Tunnel doesn't require an
   account for a quick ad-hoc tunnel, ngrok's free tier does.
4. Share the generated `https://*.trycloudflare.com` (or `*.ngrok-free.app`)
   URL.

**Tradeoffs vs. Docker**: this gets you the *full* local dataset (not
just what's bundled in the image — though Option A now also has the full
2,050-symbol set, so this gap has closed) and requires zero rebuild, but
it only works while your machine and the tunnel session are alive, and
some corporate networks block ngrok/Cloudflare Tunnel domains outright —
a real risk if the interviewer is on a locked-down work laptop. **Option
A is the safer default; use Option B only if you specifically want a
live, synchronous walkthrough rather than a "here, try it yourself"
link.**

## What's actually bundled vs. what's still external

- `market_data/` (in the repo, used by Docker): the full ~2,050-symbol
  partitioned parquet dataset — real data, matches the resume claim.
- Not bundled: the `nse_numba_backtester` sibling project referenced in
  `WALKTHROUGH.md` (the Numba-JIT execution engine this project composes
  with) — that's a separate repo/demo, not part of this container.

## Known limitations (from WALKTHROUGH.md — still true, worth restating
before a live demo)

- Not exhaustively tested across all 40+ registered indicator functions.
- `executeStrategyFullScale` in the frontend calls a `/execute-full-scale`
  route that doesn't exist on the backend — dead code, nothing in the UI
  calls it (`NewStrategy.vue` only calls `executeStrategyMultiLookahead`,
  which is what's verified working above).
- Repo has real dead weight (`junk/dead/`) — not part of the Docker
  build (excluded via `.dockerignore`), but if demoing the raw source
  tree directly, say up front that `app.py`/`App.vue` are the live files.

## Files added for this

- `webapi/Dockerfile` — backend image (micromamba base, for a reliable
  prebuilt TA-Lib binary rather than compiling the C library from
  source in a plain `python:slim` image).
- `alpha-strategy-frontend/Dockerfile` — multi-stage Node build → nginx.
- `docker-compose.yml` — wires both together, publishes 8000/5173.
- `.dockerignore` (root + frontend) — keeps `junk/`, `node_modules/`,
  `__pycache__/` etc. out of the build context.
- `scripts/build_demo_data.py` — regenerates a small 6-symbol demo
  dataset from the local NSE CSVs in `old/backtesting_engine/data` if
  you ever want a lighter image than the full 351MB dataset (not used
  by default — the current Dockerfile bundles the full set instead).
