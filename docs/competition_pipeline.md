# Competition Pipeline

近赤外スペクトルから含水率を予測するための実戦用パイプラインです。

## 実行

軽量な疎通確認:

```bash
./.venv/bin/python -u -m src.train_competition --config configs/exp003_smoke.yaml
```

堅牢型候補:

```bash
qsub jobs/competition_exp004.sh
```

攻め型候補:

```bash
qsub jobs/competition_exp005.sh
```

EDAから2候補の学習までまとめて実行:

```bash
qsub jobs/competition_full_pipeline.sh
```

EXP-004を学習してそのままSIGNATEへ提出:

```bash
qsub jobs/competition_submit_exp004.sh
```

## 構成

- `src/competition_io.py`: CSV読み込み、波数列抽出、提出CSV生成。
- `src/preprocessing.py`: SNV、MSC、Savitzky-Golay、微分。
- `src/features.py`: スペクトル統計、バンド特徴、PCA、メタ特徴。
- `src/models.py`: Ridge、PLS、KernelRidge、GBDT、LightGBM、CatBoost。
- `src/train_competition.py`: CLI エントリ（`MPLCONFIGDIR` 設定後に `run_experiment` を呼ぶ）。
- `src/experiment.py`: 実験オーケストレーション（データ読込、特徴量、学習ループ、提出）。
- `src/cv.py` / `src/metrics.py` / `src/evaluation.py` / `src/tuning.py` / `src/ensemble.py` / `src/outputs.py`: CV 分割、指標、fold 学習、Optuna、重み付き合成、成果物保存。

## 検証方針

trainとtestの樹種が分かれているため、主評価は `species number` をgroupにしたGroupKFoldです。通常KFoldだけでは同一樹種内の乾燥系列をまたいで評価し、公開LBより楽観的になる可能性があります。

## 出力

各実験は `outputs/experiments/EXP-XXX/` に以下を保存します。

- `model_summary.csv`: モデル別CV RMSEとアンサンブル重み。
- `fold_scores.csv`: fold別RMSEと検証樹種。
- `oof_predictions.csv`: OOF予測。
- `test_predictions.csv`: test予測。
- `feature_columns.csv`: 使用特徴量。
- `metadata.json`: 実験メタ情報。

提出CSVは `outputs/submissions/` にヘッダなし2列で保存します。
