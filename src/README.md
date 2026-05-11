# src

再利用する Python コード本体を置くフォルダです。  
前処理、学習、評価、提出までのロジックをモジュール（`.py` ファイル）に分けています。

## 初学者向け

**各ファイルが何をするか**のやさしい説明は、リポジトリ直下から見て  
[docs/beginner_project_guide.md](../docs/beginner_project_guide.md)  
にまとめています。初めて触るときはそちらを先に読むと全体像がつかみやすいです。

## ざっくり対応表

| ファイル | 役割の一言 |
|----------|------------|
| `train_competition.py` | 実験実行の CLI 入口 |
| `experiment.py` | 実験 1 回分の処理の流れ（司令塔） |
| `competition_io.py` | CSV 読込・提出書き出し |
| `preprocessing.py` / `features.py` | スペクトル前処理・特徴量表の作成 |
| `models.py` | モデル名から学習器を組み立て |
| `cv.py` / `metrics.py` | 交差検証の分割・RMSE |
| `evaluation.py` | fold 学習と OOF / テスト予測 |
| `tuning.py` | Optuna による LightGBM 探索（任意） |
| `ensemble.py` | 複数モデルの合成とクリップ |
| `outputs.py` | 実験フォルダへの CSV / JSON など保存 |
| `baseline.py` | 最も単純な提出例（CV なし） |
| `__init__.py` | `src` をパッケージとして扱うためのファイル |
