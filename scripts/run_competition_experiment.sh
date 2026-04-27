#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

CONFIG_PATH="${1:-configs/exp004_robust_groupcv.yaml}"

if [[ -x ./.venv/bin/python ]]; then
  PYTHON=./.venv/bin/python
else
  PYTHON=python
fi

"${PYTHON}" -u -m src.train_competition --config "${CONFIG_PATH}"
