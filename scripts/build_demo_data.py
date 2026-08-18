"""
Builds a small, real, self-contained demo dataset for alpha_strategy_parser.

The production backend expects a directory of `{SYMBOL}.parquet` files, each
with lowercase columns: date, open, high, low, close, volume (see webapi/app.py
DATA_PARTITIONED_PATH handling and FunctionRegistry._data_access).

The real ~2,050-symbol dataset lives in a sibling project on the dev machine
and isn't part of this repo. This script converts the 6 real NSE daily OHLCV
CSVs that already ship in ../old/backtesting_engine/data (BHARTIARTL, HDFCBANK,
ICICIBANK, INFY, NIFTY, RELIANCE) into that exact parquet format, so the repo
is fully self-contained and runnable by anyone who clones it -- real market
data, just a 6-symbol universe instead of 2,050.

Usage:
    python scripts/build_demo_data.py
"""
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = REPO_ROOT.parent / "old" / "backtesting_engine" / "data"
OUT_DIR = REPO_ROOT / "demo_data"

SYMBOLS = ["BHARTIARTL", "HDFCBANK", "ICICIBANK", "INFY", "NIFTY", "RELIANCE"]


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    if not SOURCE_DIR.exists():
        print(f"ERROR: source data directory not found: {SOURCE_DIR}")
        print("This script must be run on a machine that has the "
              "old/backtesting_engine/data CSVs (only needed once, to build "
              "demo_data/ -- the resulting parquet files are what actually "
              "ship in the repo/Docker image).")
        sys.exit(1)

    written = []
    for symbol in SYMBOLS:
        src = SOURCE_DIR / f"{symbol}.csv"
        if not src.exists():
            print(f"  skip {symbol}: {src} not found")
            continue
        df = pd.read_csv(src, parse_dates=["date"])
        df = df[["date", "open", "high", "low", "close", "volume"]].sort_values("date")
        df = df.reset_index(drop=True)

        out_path = OUT_DIR / f"{symbol}.parquet"
        df.to_parquet(out_path, index=False)
        written.append((symbol, len(df), out_path))
        print(f"  wrote {out_path.name}: {len(df)} rows, "
              f"{df['date'].min().date()} -> {df['date'].max().date()}")

    print(f"\nDone. {len(written)} symbols written to {OUT_DIR}")


if __name__ == "__main__":
    main()
