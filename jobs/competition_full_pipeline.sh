#!/bin/bash
#$ -cwd
#$ -q h.q
#$ -l mem_req=32g
#$ -l h_vmem=32g
#$ -l gpu=1
#$ -o logs/
#$ -e logs/

set -euo pipefail

./.venv/bin/python -u scripts/make_eda_report.py
./.venv/bin/python -u -m src.train_competition --config configs/exp003_smoke.yaml
./.venv/bin/python -u -m src.train_competition --config configs/exp004_robust_groupcv.yaml

echo "Full competition pipeline finished."
