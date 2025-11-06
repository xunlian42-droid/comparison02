#!/usr/bin/env python3
import argparse
import json
import os
import re
from glob import glob
from pathlib import Path
from bs4 import BeautifulSoup

def safe_anchor(s: str) -> str:
    if not s:
        return ""
    s = str(s).strip()
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'[\/#?&%]', '-', s)
    s = re.sub(r'[<>:"\'\[\]\(\)\{\}@!,$\^=+;：，。、・]', '', s)
    return s if s else 'work-' + re.sub(r'[^0-9a-zA-Z_-]', '', str(hash(s)))

def scan_file(path: Path):
    results = {}
    text = path.read_text(encoding='utf-8', errors='replace')
    soup = BeautifulSoup(text, 'html.parser')

    # タグページのスキャン（div.row-*）
    for div in soup.find_all('div', class_=lambda x: x and x.startswith('row-')):
        work_id = div.get('id')
        if work_id:
            title = div.find('h3')
            if title:
                title_text = title.get_text().strip()
                anchor = safe_anchor(work_id)
                results[work_id] = {"raw": title_text, "anchor": anchor}

    # 比較ページのスキャン
    if not results:
        # まず、tableの中のタイトル行をスキャン
        for tr in soup.find_all('tr'):
            tr_id = tr.get('id')
            if tr_id:
                anchor = safe_anchor(tr_id)
                results[tr_id.strip()] = {"raw": tr_id.strip(), "anchor": anchor}
                continue
            
            # title-linkクラスを持つaタグを検索
            a = tr.find('a', class_='title-link')
            if a:
                data_id = a.get('data-id') or a.get('id')
                text_key = (a.get_text() or '').strip()
                key = data_id or text_key
                if key:
                    anchor = safe_anchor(key)
                    results[key.strip()] = {"raw": key.strip(), "anchor": anchor}

        # バックアップ：単独のtitle-linkをスキャン
        if not results:
            for a in soup.find_all('a', class_='title-link'):
                data_id = a.get('data-id') or a.get('id')
                text_key = (a.get_text() or '').strip()
                key = data_id or text_key
                if key:
                    anchor = safe_anchor(key)
                    results[key.strip()] = {"raw": key.strip(), "anchor": anchor}

    return results

def build_popup_map(tags_dir: Path, pattern: str = "*.html"):
    popup_map = {}
    # タグファイルのパスを取得（完全パス）
    tag_files = sorted(glob(str(tags_dir / pattern)))
    print(f"Finding tag files in: {tags_dir}")
    print(f"Found {len(tag_files)} tag files")
    
    for f in tag_files:
        path = Path(f)
        popup_name = path.name
        # URLパスを生成（Djangoのテンプレートパスと一致させる）
        popup_path = f"comparison/tags_html_folder/{popup_name}"
        print(f"Processing {popup_name}")
        
        # ファイル内の作品情報をスキャン
        anchors = scan_file(path)
        print(f"Found {len(anchors)} anchors in {popup_name}")
        
        # 各作品のアンカーとポップアップパスを関連付け
        for key, info in anchors.items():
            popup_map[info["anchor"]] = popup_path
    
    print(f"Total popup mappings: {len(popup_map)}")
    return popup_map

def main():
    parser = argparse.ArgumentParser(description="比較ページ HTML から workPageMap JSON を生成する")
    parser.add_argument('--input-dir', '-i', default='.', help='comparison_*.html を含むディレクトリ')
    parser.add_argument('--pattern', '-p', default='**/comparison_*.html', help='比較ページの glob パターン')
    parser.add_argument('--tags-dir', '-t', default='comparison/tags_html_folder', help='タグページのディレクトリ')
    parser.add_argument('--output', '-o', default='workPageMap.json', help='出力する JSON ファイル')
    parser.add_argument('--force-override', action='store_true', help='同じキーがある場合、後のファイルで上書きする')
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    tags_dir = Path(args.tags_dir)
    files = sorted(glob(str(input_dir / args.pattern), recursive=True))
    if not files:
        print("比較ページが見つかりません。--input-dir と --pattern を確認してください。")
        return 1

    print(f"\nProcessing comparison pages from: {input_dir}")
    print(f"Found {len(files)} comparison pages")
    
    # タグページのマッピングを構築
    popup_map = build_popup_map(tags_dir)
    mapping = {}

    # 比較ページから作品情報を収集
    for f in files:
        path = Path(f)
        print(f"\nProcessing comparison page: {path.name}")
        
        anchors = scan_file(path)
        relative_path = str(path.relative_to(input_dir)).replace(os.sep, "/")
        print(f"Found {len(anchors)} works in {path.name}")
        
        for work_key, info in anchors.items():
            if work_key in mapping and not args.force_override:
                continue
            
            anchor = info["anchor"]
            title = info["raw"]  # タイトルを追加
            popup_path = popup_map.get(anchor)
            
            if popup_path:
                print(f"Found popup mapping for {work_key}: {popup_path}")
            
            mapping[work_key] = {
                "work": title,     # タイトルを設定
                "page": relative_path,
                "popup": popup_path
            }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote {len(mapping)} entries to {out.resolve()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())