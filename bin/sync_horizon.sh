#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JIANWEI_WEB_DIR="${JIANWEI_WEB_DIR:-$ROOT_DIR}"
HORIZON_DIR="${HORIZON_DIR:-$(cd "$JIANWEI_WEB_DIR/../Horizon" && pwd)}"

PERSONA_SLUG="${PERSONA_SLUG:-indie-maker}"
HOURS="${HOURS:-24}"
LIMIT="${LIMIT:-100}"
MIN_SCORE="${MIN_SCORE:-}"

HORIZON_PYTHON="${HORIZON_PYTHON:-$HORIZON_DIR/.venv/bin/python}"
JIANWEI_PYTHON="${JIANWEI_PYTHON:-$JIANWEI_WEB_DIR/.venv/bin/python}"

LOG_DIR="${LOG_DIR:-$JIANWEI_WEB_DIR/logs}"
LOG_FILE="${LOG_FILE:-$LOG_DIR/sync_horizon.log}"
LOCK_FILE="${LOCK_FILE:-$LOG_DIR/sync_horizon.lock}"

mkdir -p "$LOG_DIR"
exec >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] sync_horizon started"

if command -v flock >/dev/null 2>&1; then
  exec 9>"$LOCK_FILE"
  if ! flock -n 9; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] another sync_horizon process is running; exit"
    exit 0
  fi
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] warning: flock not found; running without lock"
fi

if [ ! -x "$HORIZON_PYTHON" ]; then
  echo "Horizon python not found or not executable: $HORIZON_PYTHON"
  exit 1
fi

if [ ! -x "$JIANWEI_PYTHON" ]; then
  echo "Jianwei python not found or not executable: $JIANWEI_PYTHON"
  exit 1
fi

cd "$HORIZON_DIR"
horizon_cmd=(
  "$HORIZON_PYTHON"
  -m src.integrations.jianwei
  --persona-slug "$PERSONA_SLUG"
  --hours "$HOURS"
  --limit "$LIMIT"
)

if [ -n "$MIN_SCORE" ]; then
  horizon_cmd+=(--min-score "$MIN_SCORE")
fi

"${horizon_cmd[@]}"

artifact_date="$("$HORIZON_PYTHON" -c 'from src.integrations.jianwei import artifact_date_for_display_timezone; print(artifact_date_for_display_timezone())')"
artifact_dir="$HORIZON_DIR/data/jianwei_artifacts/$artifact_date/$PERSONA_SLUG"

if [ ! -d "$artifact_dir" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] no artifact directory found: $artifact_dir"
  exit 0
fi

if ! find "$artifact_dir" -maxdepth 1 -type f -name "*.json" | grep -q .; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] no artifact json files found: $artifact_dir"
  exit 0
fi

cd "$JIANWEI_WEB_DIR"
./bin/import_artifacts.sh "$artifact_dir"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] sync_horizon finished"
