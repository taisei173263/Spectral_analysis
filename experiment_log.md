# Experiment Log

実験IDごとの実行メモを残す台帳です。  
最低限「設定ファイル」「スコア」「提出有無」を記録します。

| Exp ID | Config | CV/Local Score | Public Score | Notes |
|---|---|---:|---:|---|
| EXP-001 | `configs/exp001_baseline.yaml` | - | - | 初期ダミー |
| EXP-002 | `configs/exp002_feature_trial.yaml` | - | - | 特徴量試行ダミー |
| EXP-003 | `configs/exp003_smoke.yaml` | 42.94447 | - | 実戦パイプライン疎通確認。提出CSV生成済み |
| EXP-004 | `configs/exp004_robust_groupcv.yaml` | 30.68512 | submitted | GroupKFold重視の堅牢型候補。`outputs/submissions/exp004_robust_submission.csv` をSIGNATE提出済み |
| EXP-005 | `configs/exp005_attack_optuna.yaml` | pending | - | メタ特徴量とOptunaを含む攻め型候補。`jobs/competition_exp005.sh` で追加実行可能 |
