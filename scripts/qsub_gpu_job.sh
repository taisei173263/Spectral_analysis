#!/usr/bin/env bash
#$ -S /bin/bash
#$ -cwd
#$ -j y
#$ -o logs/qsub_gpu.$JOB_ID.log
#$ -q t.q
#$ -l gpu=1
#$ -l mem_req=32G
#$ -l h_rt=12:00:00
#$ -pe smp 8

set -euo pipefail

cd /home/taisei/Spectral_analysis
source .venv/bin/activate

echo "[INFO] host=$(hostname) job_id=${JOB_ID:-N/A} started_at=$(date '+%F %T')"
nvidia-smi || true

# 必要な処理に置き換えてください
python -m src.baseline --config config/default.yaml

echo "[INFO] finished_at=$(date '+%F %T')"
