# SIGNATE CLI運用メモ

## 初回認証
```bash
source .venv/bin/activate
signate token -e your_email@example.com
```

## 投稿対象の確認
```bash
signate competition-list
signate task-list --competition_key=<competition_public_key>
signate file-list --task_key=<task_public_key>
```

## データ取得
```bash
signate download --task_key=<task_public_key> --file_key=<file_public_key> --path=/tmp/dataset.zip
```

## 提出
```bash
python -m src.baseline --config config/default.yaml
bash scripts/submit_signate.sh <task_public_key> outputs/submissions/baseline_submission.csv "first submit"
```
