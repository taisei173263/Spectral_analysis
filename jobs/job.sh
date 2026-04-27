#!/bin/bash
#$ -cwd
#$ -q h.q
#$ -l mem_req=16g
#$ -l h_vmem=16g
#$ -l gpu=1
#$ -o logs/
#$ -e logs/

set -euo pipefail

./.venv/bin/python -u -m src.baseline --config config/default.yaml
