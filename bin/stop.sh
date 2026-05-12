#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PID_FILE="${PID_FILE:-runtime/jianwei.pid}"

if [ ! -f "$PID_FILE" ]; then
  echo "未找到 PID 文件，见微可能没有通过 bin/start.sh 启动。"
  echo "如果需要手动查找进程，可以执行：ps aux | grep 'uvicorn app.main:app'"
  exit 0
fi

PID="$(cat "$PID_FILE")"

if [ -z "$PID" ] || ! kill -0 "$PID" 2>/dev/null; then
  echo "PID $PID 不存在，清理 PID 文件。"
  rm -f "$PID_FILE"
  exit 0
fi

kill "$PID"

for _ in $(seq 1 10); do
  if ! kill -0 "$PID" 2>/dev/null; then
    rm -f "$PID_FILE"
    echo "见微已停止，PID: $PID"
    exit 0
  fi
  sleep 1
done

echo "进程未正常退出，执行强制停止，PID: $PID"
kill -9 "$PID" 2>/dev/null || true
rm -f "$PID_FILE"
echo "见微已停止。"
