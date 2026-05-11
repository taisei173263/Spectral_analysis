# configs

**実験（exp）ごとの設定**を YAML で置くフォルダです。

- ファイル名の例: `exp003_smoke.yaml`, `exp004_robust_groupcv.yaml`
- 中身の例: データのパス、交差検証の方法、使うモデルとパラメータ、出力先など

実行するときは、次のように **どの YAML を使うか** を指定します。

```bash
python -m src.train_competition --config configs/exp003_smoke.yaml
```

親フォルダの `config/`（単数形）には、**共通の薄い設定**（baseline 用の `default.yaml` など）を置く想定です。  
`config/` と `configs/` の違いがわからなくなったら、[docs/beginner_project_guide.md](../docs/beginner_project_guide.md) の「プロジェクトの他のフォルダ」を読んでください。
