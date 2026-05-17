#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

IMPORT_DATE="${IMPORT_DATE:-}"

if [ "$#" -ne 1 ]; then
  echo "Usage: ./bin/import_artifacts.sh <artifact-json-file-or-directory>"
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Missing .venv/bin/python. Please create the virtual environment and install dependencies first."
  exit 1
fi

if [ -n "$IMPORT_DATE" ]; then
  ".venv/bin/python" -m app.worker.import_artifact "$1" --import-date "$IMPORT_DATE"
else
  ".venv/bin/python" -m app.worker.import_artifact "$1"
fi
