# jobs

計算クラスタ（AGE / SGE など）に **`qsub` で投入するシェルスクリプト**を置くフォルダです。

- `competition_*.sh`: 学習やパイプラインをノード上で実行する例
- `job.sh`: 汎用テンプレート
- [JOB_SCRIPT_GUIDE.md](JOB_SCRIPT_GUIDE.md): スクリプト各行の意味（この環境では `./.venv/bin/python` を使うなど）

ローカル PC で試すだけなら、まずは `python -m src.train_competition --config ...` で十分です。  
クラスタに慣れてから、このフォルダのスクリプトを参考にするとよいです。

プロジェクト全体の地図は [docs/beginner_project_guide.md](../docs/beginner_project_guide.md) も参照してください。
