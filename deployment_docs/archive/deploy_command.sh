#!/bin/bash

# Simple deployment command
# Run this to set up your testing environment

echo "🚀 Setting up Alpha Strategy Parser..."
echo "======================================"

# Check if we're in the right directory
if [ ! -f "src/function_registry.py" ]; then
    echo "❌ Please run this from the alpha_strategy_parser directory"
    echo "💡 cd to alpha_strategy_parser first"
    exit 1
fi

# Run the full deployment script
./deploy.sh

echo ""
echo "🎯 Quick commands after deployment:"
echo "  source venv/bin/activate    # Activate environment"
echo "  python quick_start.py       # Quick test"
echo "  python demo_final_comprehensive.py  # Full demo"
echo "  cat docs/USER_GUIDE.md      # View user guide" 

# compact-history: run JSONL->Parquet and Parquet->DuckDB
compact_history() {
  BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
  WEBAPI_DIR="$BASE_DIR/webapi"
  HISTORY_DIR="$BASE_DIR/history"
  VENV_ACTIVATE="$BASE_DIR/venv/bin/activate"
  if [ -f "$VENV_ACTIVATE" ]; then
    # shellcheck disable=SC1090
    . "$VENV_ACTIVATE"
  fi
  python - <<'PY'
import os, sys
BASE = "/home/miso/Documents/SID/alpha_parser_project_analysis/alpha_strategy_parser"
sys.path.insert(0, os.path.join(BASE, 'webapi'))
from compact_history import compact_jsonl_to_parquet_and_duckdb, update_duckdb_from_parquet
HISTORY = os.path.join(BASE, 'history')
compact_jsonl_to_parquet_and_duckdb(history_root=HISTORY)
parquet_glob = os.path.join(HISTORY, 'parquet', 'dt=*', 'runs.parquet')
update_duckdb_from_parquet(db_path=os.path.join(HISTORY, 'history.duckdb'), parquet_glob=parquet_glob)
print('OK: history compacted and DuckDB updated')
PY
} 