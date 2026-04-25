#!/bin/bash
#$ -cwd
#$ -q tsmall
#$ -l mem_req=16g
#$ -l h_vmem=16g
#$ -l gpu=1

set -euo pipefail

uv run python -u main.py
