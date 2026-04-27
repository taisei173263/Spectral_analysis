# `jobs/job.sh` ガイド

このファイルは、AGE/SGE 環境で `qsub jobs/job.sh` を実行するときの最小テンプレートと、各行の意味をまとめたものです。

## 現在の `job.sh`

```bash
#!/bin/bash
#$ -cwd
#$ -q h.q
#$ -l mem_req=16g
#$ -l h_vmem=16g
#$ -l gpu=1
#$ -o logs/
#$ -e logs/

set -euo pipefail

./.venv/bin/python -u -m src.baseline --config config/default.yaml
```

## 各行の意味

- `#!/bin/bash`  
  このジョブスクリプトを Bash で実行します。

- `#$ -cwd`  
  `qsub` を実行したカレントディレクトリでジョブを実行します。  
  このリポジトリでは通常 `/home/taisei/Spectral_analysis` です。

- `#$ -q h.q`  
  投入先キューを指定します。環境によって使えるキューは異なります。

- `#$ -l mem_req=16g`  
  スケジューラに要求するメモリ量です（16GB）。

- `#$ -l h_vmem=16g`  
  プロセスのメモリ上限です。超えるとジョブが落ちることがあります。

- `#$ -l gpu=1`  
  GPU を 1 枚要求します。

- `#$ -o logs/`  
  標準出力ログ（`job.sh.o<jobid>`）の出力先ディレクトリを指定します。

- `#$ -e logs/`  
  標準エラーログ（`job.sh.e<jobid>`）の出力先ディレクトリを指定します。

- `set -euo pipefail`  
  シェルの安全設定です。  
  - `-e`: エラー時に即終了  
  - `-u`: 未定義変数をエラーにする  
  - `-o pipefail`: パイプの途中失敗も検知する

- `./.venv/bin/python -u -m src.baseline --config config/default.yaml`  
  仮想環境の Python を直接使ってベースラインを実行します。  
  `-u` はログをバッファせずに出力するため、進捗確認がしやすくなります。

## よくある失敗と対処

### 1) `bash: uv: command not found`
計算ノードで `uv` が PATH にないと発生します。  
このリポジトリでは `uv run ...` ではなく、`./.venv/bin/python ...` を使うのが安全です。

### 2) `^M` が出る（CRLF エラー）
`job.sh` が CRLF 改行だと Bash が解釈に失敗します。  
必ず LF 改行で保存してください。

### 3) ジョブが `qw` のまま進まない
主にキュー混雑、GPU空き不足、リソース要求が厳しいときに起きます。  
`qstat -j <jobid>` で待ち理由を確認します。

## 基本コマンド

```bash
# ジョブ投入
qsub jobs/job.sh

# 自分のジョブ一覧
qstat -u "$USER"

# 詳細
qstat -j <jobid>

# 終了済みジョブの実行情報
qacct -j <jobid>
```
