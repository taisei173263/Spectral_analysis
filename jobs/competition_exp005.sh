#!/bin/bash
#$ -cwd
#$ -q h.q
#$ -l mem_req=48g
#$ -l h_vmem=48g
#$ -l gpu=1
#$ -o logs/
#$ -e logs/

set -euo pipefail

./.venv/bin/python -u -m src.train_competition --config configs/exp005_attack_optuna.yaml
