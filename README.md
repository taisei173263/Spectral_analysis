# Spectral Analysis Competition Starter

SIGNATE CLI で提出まで行える最小構成のスターターです。

## 1. セットアップ
```bash
bash scripts/setup.sh
source .venv/bin/activate
```

## 2. SIGNATE CLI 認証
```bash
signate --version
signate token -e <your_email@example.com>
```

認証後に以下が通ることを確認します。
```bash
signate competition-list
signate task-list --competition_key=<competition_public_key>
```

## 3. データ配置
既存データは `data/raw/` に置く想定です。

- `data/raw/train.csv`
- `data/raw/test.csv`
- `data/raw/sample_submit.csv`

## 4. ベースライン提出ファイル作成
```bash
python -m src.baseline --config config/default.yaml
```

出力先:
- `outputs/submissions/baseline_submission.csv`

## 5. 提出
```bash
bash scripts/submit_signate.sh <task_public_key> outputs/submissions/baseline_submission.csv "baseline submit"
```

## 6. GPUジョブ実行（AGE/SGE: qsub/qstat）
この環境は PBS ではなく AGE/SGE 系です。  
GPUは `qsub` で `-l gpu=<数>` を指定して要求します。

```bash
# GPU状況
qstat -f -F gpu

# テンプレートジョブ投入
qsub scripts/qsub_gpu_job.sh

# 自分のジョブ確認
qstat -u "$USER"
```

詳細コマンド集は `docs/cluster_gpu_commands.md` を参照してください。  
`job.sh` 実行から提出までの一連手順は `docs/job_to_submit_flow.md` にまとめています。

## ディレクトリ構成
```text
.
├── config/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── logs/
├── models/
├── notebooks/
├── outputs/
│   └── submissions/
├── scripts/
├── src/
└── tests/
```

## テスト
```bash
pytest -q
```
