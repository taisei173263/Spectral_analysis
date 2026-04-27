#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

CONFIG_PATH="${1:-configs/exp004_robust_groupcv.yaml}"
TASK_KEY="${2:-8940dcfa70434a6aaaa28d661652d536}"
MEMO="${3:-competition pipeline submit}"

bash scripts/run_competition_experiment.sh "${CONFIG_PATH}"

SUBMISSION_PATH="$(
  python - <<'PY' "${CONFIG_PATH}"
from pathlib import Path
import sys
import yaml

with Path(sys.argv[1]).open("r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
print(config["paths"]["output_submission_csv"])
PY
)"

bash scripts/submit_signate.sh "${TASK_KEY}" "${SUBMISSION_PATH}" "${MEMO}"
