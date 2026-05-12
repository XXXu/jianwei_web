#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PID_FILE="${PID_FILE:-runtime/jianwei.pid}"
LOG_FILE="${LOG_FILE:-logs/jianwei.log}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

mkdir -p "$(dirname "$PID_FILE")" "$(dirname "$LOG_FILE")" data

if [ -f "$PID_FILE" ]; then
  PID="$(cat "$PID_FILE")"
  if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
    echo "见微已经在运行，PID: $PID"
    exit 0
  fi
  rm -f "$PID_FILE"
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "未找到 .venv/bin/python，请先创建虚拟环境并安装依赖。"
  echo "示例：python3 -m venv .venv && source .venv/bin/activate && python -m pip install -e ."
  exit 1
fi

".venv/bin/python" -m alembic upgrade head
".venv/bin/python" -m app.seed

nohup ".venv/bin/python" -m uvicorn app.main:app --host "$HOST" --port "$PORT" > "$LOG_FILE" 2>&1 &
PID="$!"
echo "$PID" > "$PID_FILE"

echo "见微已启动，PID: $PID"
echo "监听地址: http://$HOST:$PORT"
echo "日志文件: $LOG_FILE"
