#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_DIR="$(cd "$ROOT_DIR/.." && pwd)"

UPLOAD_ROOT="${UPLOAD_ROOT:-$WORKSPACE_DIR/artifacts}"
PERSONA_SLUG="${PERSONA_SLUG:-indie-maker}"
IMPORT_DATE="${1:-${IMPORT_DATE:-}}"

if [ -z "$IMPORT_DATE" ]; then
  latest_dir="$(find "$UPLOAD_ROOT" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | tail -n 1 || true)"
  if [ -z "$latest_dir" ]; then
    echo "No uploaded artifact directory found: $UPLOAD_ROOT"
    exit 1
  fi
  IMPORT_DATE="$(basename "$latest_dir")"
fi

artifact_dir="$UPLOAD_ROOT/$IMPORT_DATE/$PERSONA_SLUG"

if [ ! -d "$artifact_dir" ]; then
  echo "Artifact directory not found: $artifact_dir"
  exit 1
fi

if ! find "$artifact_dir" -maxdepth 1 -type f -name "*.json" | grep -q .; then
  echo "No JSON files found in artifact directory: $artifact_dir"
  exit 1
fi

echo "Importing artifacts: $artifact_dir"
IMPORT_DATE="$IMPORT_DATE" bash "$ROOT_DIR/bin/import_artifacts.sh" "$artifact_dir"
