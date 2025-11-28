import os
import json
from bs4 import BeautifulSoup

# 比較表HTMLがあるディレクトリ
BASE_DIR = 'comparison/templates/comparison/comparison_gojuon_with_links'

# 対象ファイル名（01〜10）
kana_list = ['a', 'ka', 'sa', 'ta', 'na', 'ha', 'ma', 'ya', 'ra', 'wa']
filenames = [
    f'comparison_{i:02d}_{kana}_with_links.html'
    for i, kana in enumerate(kana_list, start=1)
]

# マッピングファイル（external_id → work.id）
MAPPING_FILE = 'external_to_work_id.json'

# JSON を読み込む
with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
    external_to_work_id = json.load(f)

def ensure_fav_cell_in_tr(soup, tr):
    if tr.find('td', class_='fav-cell'):
        return False
    new_td = soup.new_tag('td')
    new_td['class'] = 'fav-cell'
    new_td.string = ''
    first_td = tr.find('td')
    if first_td:
        first_td.insert_before(new_td)
    else:
        tr.append(new_td)
    return True

def inject_work_id_to_title_link(a_tag):
    ext_id = a_tag.get('data-id')
    if not ext_id:
        return False
    work_id = external_to_work_id.get(ext_id)
    if not work_id:
        return False
    a_tag['data-work-id'] = str(work_id)
    return True

import re

def normalize_text(text: str) -> str:
    # 改行・タブをスペースに
    text = re.sub(r'[\n\r\t]+', ' ', text)
    # 連続スペースを1つに
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    changed_rows = 0
    updated_links = 0

    for tr in soup.find_all('tr'):
        if tr.find('th'):
            continue

        if ensure_fav_cell_in_tr(soup, tr):
            changed_rows += 1

        a_tag = tr.find('a', class_='title-link')
        if a_tag:
            # テキストを正規化
            a_tag.string = normalize_text(a_tag.get_text())
            if inject_work_id_to_title_link(a_tag):
                updated_links += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print(f'✅ {os.path.basename(output_path)} 完了')
    print(f'  fav-cell 追加: {changed_rows} 行')
    print(f'  data-work-id 追加: {updated_links} 件')

# 全ファイルを処理
for fname in filenames:
    input_path = os.path.join(BASE_DIR, fname)
    # output_path = os.path.join(BASE_DIR, fname.replace('_with_links.html', '_with_links_with_fav.html'))

    # 出力ファイルを同じパスにする（上書き保存）
    output_path = input_path
    if not os.path.exists(input_path):
        print(f'⚠️ スキップ（ファイルなし）: {input_path}')
        continue
    process_file(input_path, output_path)


print('🎉 全ファイルの処理が完了しました')