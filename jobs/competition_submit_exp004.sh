#!/bin/bash
#$ -cwd
#$ -q h.q
#$ -l mem_req=32g
#$ -l h_vmem=32g
#$ -l gpu=1
#$ -o logs/
#$ -e logs/

set -euo pipefail

./.venv/bin/python -u -m src.train_competition --config configs/exp004_robust_groupcv.yaml
bash scripts/submit_signate.sh 8940dcfa70434a6aaaa28d661652d536 \
  outputs/submissions/exp004_robust_submission.csv \
  "EXP-004 robust groupcv ensemble"
