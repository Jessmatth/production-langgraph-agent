#!/usr/bin/env bash
# Run full verification after GCP setup and: gcloud auth application-default login
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -f .env ]]; then
  echo "Copy .env.example to .env and fill in GCP values."
  exit 1
fi

PYTHON="${PYTHON:-.venv/bin/python}"
if [[ ! -x "$PYTHON" ]]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
  PYTHON=".venv/bin/python"
fi

echo "==> Local query"
"$PYTHON" deploy.py local --prompt "Get product details for headphones"

echo "==> Deploy"
"$PYTHON" deploy.py deploy

echo "==> Remote query"
"$PYTHON" deploy.py query --prompt "Get product details for shoes"

echo "==> Delete"
"$PYTHON" deploy.py delete

echo "All checks passed."
