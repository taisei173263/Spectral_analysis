# Spectral Analysis Competition Starter
常木のブランチ
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

今回提出したコンペ情報（固定値）:
- competition_key: `37308d147238487c96551300b8e4cb76`（近赤外研究会 スペクトル分析チャレンジ）
- task_key: `8940dcfa70434a6aaaa28d661652d536`（木材含水率予測）

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

今回の提出例:
```bash
source .venv/bin/activate
bash scripts/submit_signate.sh 8940dcfa70434a6aaaa28d661652d536 outputs/submissions/baseline_submission.csv "job 531256 baseline submit"
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
`jobs/job.sh` の書き方と各行の意味は `jobs/JOB_SCRIPT_GUIDE.md` を参照してください。
コンペ実戦用パイプラインは `docs/competition_pipeline.md` を参照してください。

### job.sh 運用の注意点（この環境でハマりやすい点）
- 実行コマンドは `uv` ではなく `./.venv/bin/python` を使う  
  （計算ノードで `uv: command not found` を避けるため）
- 改行コードは LF にする  
  （CRLF だと `^M` エラーでジョブが即失敗する）
- 標準出力/標準エラーは `logs/` に出す  
  （`#$ -o logs/` と `#$ -e logs/`）

## ディレクトリ構成
```text
.
├── config/
├── configs/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── logs/
├── models/
├── notebooks/
├── outputs/
│   ├── experiments/
│   └── submissions/
├── scripts/
├── src/
├── tests/
└── experiment_log.md
```

## 実験（exp）管理ルール
- 設定は `configs/expXXX_*.yaml` に追加
- 実験結果は `outputs/experiments/EXP-XXX/` に保存
- 提出CSVは `outputs/submissions/` に保存
- 実験メモは `experiment_log.md` に追記

## テスト
```bash
pytest -q
```
