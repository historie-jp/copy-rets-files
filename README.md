# PDF Flat Copy Tool

指定したフォルダ内にある PDF ファイルを検索し、設定した出力先フォルダへフラット（階層なし）にコピーするツールです。

## 特徴

- **特定階層の検索**: 
  - ソースフォルダ直下
  - ソース直下にある「数字_」で始まるフォルダ内
- **ファイル名制限**: ファイル名が数字で始まる `.pdf` のみを対象とします。
- **ファイル名衝突回避**: コピー先に同名ファイルがある場合、自動的に `filename_1.pdf` のようにリネームします。
- **Dry Run 機能**: 実際にコピーする前に対象ファイルを確認できます。

## セットアップ

このツールは [uv](https://docs.astral.sh/uv/) を使用して依存関係を管理します。

### 1. uv のインストール

#### macOS (Homebrew)
```bash
brew install uv
```

#### Windows
PowerShell で以下のコマンドを実行します（公式サイト推奨のスタンドアロンインストーラー）：
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
または、`winget` を使用することも可能です：
```powershell
winget install astral-sh.uv
```

### 2. プロジェクトの準備
リポジトリをクローン後、以下のコマンドで環境を構築します。
```bash
uv sync
```

### 3. 設定ファイルの作成
`config.yaml.example` を `config.yaml` にコピーして、環境に合わせて設定を編集してください。
```bash
cp config.yaml.example config.yaml
```

## 使い方

### 1. 設定の変更
`config.yaml` を編集し、コピー元とコピー先のパスを指定します。

```yaml
source_dir: "./src"          # コピー元のフォルダ
destination_dir: "./output"   # コピー先のフォルダ
```

### 2. 実行

#### 動作確認 (Dry Run)
実際にファイルをコピーせず、対象となるファイルの一覧をソートして表示します。
```bash
uv run copy_pdfs.py --dry-run
```

#### 特定の番号のみコピー
コピーしたいファイルの番号（ファイル名の先頭の数字）をカンマ区切りで指定できます。
```bash
uv run copy_pdfs.py --numbers 1,5,10
```

#### 本番実行
```bash
uv run copy_pdfs.py
```

## コピーのルール
1. `src/*.pdf` (ファイル名が数字開始) -> **コピー対象**
2. `src/00_hoge/*.pdf` (フォルダ名が数字+アンダースコア、かつファイル名が数字開始) -> **コピー対象**
3. `src/abc_folder/*.pdf` -> **除外** (フォルダ名が数字開始でない)
4. `src/00_hoge/sub/*.pdf` -> **除外** (2階層以上深い)
5. `src/test.pdf` -> **除外** (ファイル名が数字開始でない)
