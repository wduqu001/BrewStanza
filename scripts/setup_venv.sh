#!/usr/bin/env bash
set -euo pipefail

# Create a virtual environment named .venv and install development dependencies.
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

cat <<'EOF'
Virtual environment created at .venv
Activate with:
  source .venv/bin/activate
To remove: rm -rf .venv
EOF
