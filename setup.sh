#!/usr/bin/env bash
# One-command environment setup (macOS / Linux).
# Usage:  bash setup.sh
set -euo pipefail

if command -v python3.12 >/dev/null 2>&1; then
  PY=python3.12
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
  echo "WARNING: python3.12 not found; using $($PY --version). Confirm it is 3.12."
else
  echo "No Python found. Install Python 3.12 first." >&2
  exit 1
fi

echo "Creating virtual environment in .venv ..."
"$PY" -m venv .venv

echo "Installing requirements ..."
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from template - add your DEEPSEEK_API_KEY."
fi

echo ""
echo "Done. Activate with:  source .venv/bin/activate"
echo "Then run tests:        pytest -q"
