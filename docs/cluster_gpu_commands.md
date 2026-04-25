# AGE(qsub/qstat) GPU運用コマンド集

この環境は PBS の `qstat -Q` ではなく、AGE/SGE 系コマンドです。  
GPU は `-l gpu=<N>` で要求します。

## 1) GPU状況の確認
```bash
qstat -f -F gpu
```

## 2) 自分のジョブ確認
```bash
qstat -u "$USER"
```

## 3) キュー一覧
```bash
qconf -sql
```

## 4) 利用可能リソース一覧（gpu 定義確認）
```bash
qconf -sc
```

## 5) GPUジョブ投入（推奨）
テンプレート:
- `scripts/qsub_gpu_job.sh`
- `job.sh`（シンプル版）

投入:
```bash
qsub scripts/qsub_gpu_job.sh
qsub job.sh
```

## 6) 1行でGPUジョブ投入（簡易）
```bash
qsub -cwd -j y -o logs/oneshot.$JOB_ID.log -q t.q -l gpu=1 -l mem_req=32G -l h_rt=12:00:00 -pe smp 8 \
  /bin/bash -lc "cd /home/taisei/Spectral_analysis && source .venv/bin/activate && python -m src.baseline --config config/default.yaml"
```

## 7) ジョブ詳細確認
```bash
qstat -j <job_id>
```

## 8) ジョブ停止
```bash
qdel <job_id>
```

## 9) ログ確認
```bash
ls -lh logs/
```

## 補足
- GPU利用可能キューは `qstat -f -F gpu` で `hc:gpu>0` のキューを選ぶ
- 現在は `t.q` に `hc:gpu=2` のノードがあり、GPU実行向けとして使いやすい
- `h.q` は一部ノードで `gpu=1` が見えます（状況に応じて `-q h.q` も可）
