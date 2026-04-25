# job.sh 実行から提出までの流れ

`job.sh` で GPU 計算を回し、結果ファイルを確認して SIGNATE CLI で提出するまでの最短手順です。

## 0. 事前準備（初回のみ）
```bash
cd /home/taisei/Spectral_analysis
bash scripts/setup.sh
source .venv/bin/activate
signate token -e <your_email@example.com>
```

## 1. GPUジョブ投入
```bash
cd /home/taisei/Spectral_analysis
source .venv/bin/activate
qsub job.sh
```

`qsub` 実行時の出力に表示される `job_id` を控えます。

## 2. 実行状況の確認
```bash
qstat -u "$USER"
qstat -j <job_id>
```

## 3. 実行完了後の結果確認
`job.sh` 内で `main.py` が保存した提出用CSVを確認します。

```bash
ls -lh outputs/submissions
```

## 4. task_key の確認（未把握の場合）
```bash
signate competition-list
signate task-list --competition_key=<competition_public_key>
```

## 5. 提出
```bash
bash scripts/submit_signate.sh <task_key> outputs/submissions/<submission_file>.csv "job.sh run"
```

または直接:
```bash
signate submit --task_key=<task_key> --path=outputs/submissions/<submission_file>.csv --memo "job.sh run"
```

## 6. よく使う補助コマンド
```bash
# GPU空き状況
qstat -f -F gpu

# ジョブ停止
qdel <job_id>
```
