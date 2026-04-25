#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "使い方: $0 <task_key> <submission_csv_path> [memo]"
  exit 1
fi

TASK_KEY="$1"
SUBMISSION_PATH="$2"
MEMO="${3:-}"

if ! command -v signate >/dev/null 2>&1; then
  echo "signate コマンドが見つかりません。'.venv' を有効化してから実行してください。"
  exit 1
fi

if [[ ! -f "${SUBMISSION_PATH}" ]]; then
  echo "提出ファイルが存在しません: ${SUBMISSION_PATH}"
  exit 1
fi

if [[ -n "${MEMO}" ]]; then
  signate submit --task_key="${TASK_KEY}" --path="${SUBMISSION_PATH}" --memo "${MEMO}"
else
  signate submit --task_key="${TASK_KEY}" --path="${SUBMISSION_PATH}"
fi
