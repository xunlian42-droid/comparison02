import os
import json
from bs4 import BeautifulSoup

# 比較表HTMLがあるディレクトリ
BASE_DIR = 'comparison/templates/comparison/comparison_gojuon_with_links'

# 対象ファイル名（01〜10）
filenames = [
    f'comparison_{i:02d}_{kana}_with_links.html'
    for i, kana in enumerate(['a', 'ka', 'sa', 'ta', 'na', 'ha', 'ma', 'ya', 'ra', 'wa'], start=1)
]

# 結果を格納する辞書
external_to_title = {}

for fname in filenames:
    path = os.path.join(BASE_DIR, fname)
    if not os.path.exists(path):
        print(f'⚠️ ファイルが見つかりません: {path}')
        continue

    with open(path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        for a in soup.find_all('a', class_='title-link'):
            ext_id = a.get('data-id')
            title = a.get_text(strip=True)
            if ext_id and title:
                external_to_title[ext_id] = title

# JSON に保存
output_path = 'external_to_title.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(external_to_title, f, ensure_ascii=False, indent=2)

print(f'✅ 書き出し完了: {output_path}')
print(f'  件数: {len(external_to_title)}')