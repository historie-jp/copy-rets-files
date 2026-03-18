import os
import shutil
import yaml
import pathlib
import argparse
import re
from typing import Dict, List

def load_config(config_path: str = "config.yaml") -> Dict[str, str]:
    """YAML設定ファイルからフォルダパスを読み込みます。"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"設定ファイル {config_path} が見つかりません。")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        if not config:
            raise ValueError("設定ファイルが空です。")
        return config

def flatten_copy_pdfs(source_dir: str, dest_dir: str, dry_run: bool = False, target_numbers: List[int] = None):
    """
    1. ソースディレクトリ直下のPDF (level 0) かつ 数字で始まるファイル
    2. ソース直下にある「数字_」で始まるフォルダ直下のPDF (level 1) かつ 数字で始まるファイル
    のみをコピー対象とします。
    target_numbers が指定されている場合、その番号で始まるファイルのみを対象とします。
    """
    source_path = pathlib.Path(source_dir)
    dest_path = pathlib.Path(dest_dir)

    print(f"\n--- {'[DRY RUN MODE]' if dry_run else '[EXECUTION MODE]'} ---")
    if target_numbers:
        print(f"指定番号: {sorted(target_numbers)}")
    print(f"ソース: {source_path.absolute()}")
    print(f"コピー先: {dest_path.absolute()}\n")

    if not dry_run:
        dest_path.mkdir(parents=True, exist_ok=True)

    target_files: List[pathlib.Path] = []

    # --- 検索処理 ---

    def is_target(f: pathlib.Path) -> bool:
        if not f.is_file() or not f.name.endswith(".pdf"):
            return False
        match = re.match(r"^(\d+)", f.name)
        if not match:
            return False
        
        if target_numbers is not None:
            file_num = int(match.group(1))
            return file_num in target_numbers
        return True

    # 1. ソース直下 (Level 0)
    for f in source_path.glob("*.pdf"):
        if is_target(f):
            target_files.append(f)

    # 2. 1階層下のフォルダ (Level 1)
    for item in source_path.iterdir():
        if item.is_dir() and re.match(r"^\d+_", item.name):
            for f in item.glob("*.pdf"):
                if is_target(f):
                    target_files.append(f)

    if not target_files:
        print("コピー対象のPDFは見つかりませんでした。")
        return

    # ファイル名でソート
    target_files.sort(key=lambda x: x.name)

    # --- コピー処理 ---
    count = 0
    for pdf_file in target_files:
        target_name = pdf_file.name
        target_path = dest_path / target_name
        
        # ファイル名重複回避
        if target_path.exists():
            stem = pdf_file.stem
            suffix = pdf_file.suffix
            counter = 1
            while target_path.exists():
                target_name = f"{stem}_{counter}{suffix}"
                target_path = dest_path / target_name
                counter += 1
        
        if dry_run:
            print(f"[WILL COPY] {pdf_file.name} (from: {pdf_file.parent.name}) -> {target_name}")
        else:
            shutil.copy2(pdf_file, target_path)
            print(f"[COPIED] {pdf_file.name} -> {target_name}")
        count += 1

    print(f"\n完了: {count} 件のファイルを処理しました。")

def main():
    parser = argparse.ArgumentParser(description="PDFをフラットにコピーします。")
    parser.add_argument("--dry-run", action="store_true", help="実際にコピーせずに対象ファイルを確認します。")
    parser.add_argument("--numbers", type=str, help="カンマ区切りでコピーしたいファイルの番号を指定します。")
    args = parser.parse_args()

    target_numbers = None
    if args.numbers:
        try:
            target_numbers = [int(n.strip()) for n in args.numbers.split(",") if n.strip()]
        except ValueError:
            print("エラー: --numbers には数字をカンマ区切りで指定してください。")
            return

    try:
        config = load_config()
        source = config.get("source_dir", "./source")
        destination = config.get("destination_dir", "./output")
        
        if not os.path.exists(source):
            print(f"エラー: ソースディレクトリ '{source}' が存在しません。")
            return

        flatten_copy_pdfs(source, destination, dry_run=args.dry_run, target_numbers=target_numbers)
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
