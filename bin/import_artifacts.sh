#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ "$#" -ne 1 ]; then
  echo "用法：./bin/import_artifacts.sh <artifact-json-file-or-directory>"
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "未找到 .venv/bin/python，请先创建虚拟环境并安装依赖。"
  exit 1
fi

".venv/bin/python" -m app.worker.import_artifact "$1"
