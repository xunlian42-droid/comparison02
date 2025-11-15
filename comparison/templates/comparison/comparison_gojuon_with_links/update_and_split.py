#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import pykakasi

_kks = pykakasi.kakasi()
_kks.setMode("K", "H")  # カタカナ→ひらがな
_conv = _kks.getConverter()

def first_hiragana_from_kana(kana: str) -> str:
    """
    与えられたカタカナ文字列をひらがなに変換し、
    先頭１文字を返すユーティリティ関数
    """
    hira = _conv.do(kana or "")
    return hira[0] if hira else ""

# 定数・設定

API_BASE = (
    "https://animestore.docomo.ne.jp/"
    "animestore/rest/v1/themes/CO00000002/works"
)
PARAMS = {
    "limit": 60,
    "sort":  "release_date",
    "_":     int(time.time() * 1000),
}
TEMP_HTML = "comparison_new_title_with_links.html"
ROW_FILES = {
    "01_a":  "comparison_01_a_with_links.html",
    "02_ka": "comparison_02_ka_with_links.html",
    "03_sa": "comparison_03_sa_with_links.html",
    "04_ta": "comparison_04_ta_with_links.html",
    "05_na": "comparison_05_na_with_links.html",
    "06_ha": "comparison_06_ha_with_links.html",
    "07_ma": "comparison_07_ma_with_links.html",
    "08_ya": "comparison_08_ya_with_links.html",
    "09_ra": "comparison_09_ra_with_links.html",
    "10_wa": "comparison_10_wa_with_links.html",
}
INITIAL_MAP = {
    **dict.fromkeys("あいうえお", "01_a"),
    **dict.fromkeys("かきくけこ", "02_ka"),
    **dict.fromkeys("さしすせそ", "03_sa"),
    **dict.fromkeys("たちつてと", "04_ta"),
    **dict.fromkeys("なにぬねの", "05_na"),
    **dict.fromkeys("はひふへほ", "06_ha"),
    **dict.fromkeys("まみむめも", "07_ma"),
    **dict.fromkeys("やゆよ",     "08_ya"),
    **dict.fromkeys("らりるれろ", "09_ra"),
    **dict.fromkeys("わをん",     "10_wa"),
}

# ユーティリティ
def safe_id(title: str) -> str:
    s = re.sub(r"[^\w一-龥ぁ-んァ-ヶ]", "_", title)
    return re.sub(r"_+", "_", s).strip("_")

def load_existing_titles() -> dict[str, bool]:
    """
    既存の五十音ファイルから
    title.lower() → dアニメリンク有無 のマップを生成
    """
    title_map: dict[str, bool] = {}
    for path in ROW_FILES.values():
        if not Path(path).exists():
            continue
        soup = BeautifulSoup(Path(path).read_text("utf-8"), "html.parser")
        # 2番目の<table>（.mark02）内<tr>だけを走査
        for tr in soup.select("table.mark02 tbody tr"):
            a = tr.select_one("a.title-link")
            title = a.text.strip()
            title_lower = title.lower()
            # 2列目<td>内に<a>があるか
            has_link = bool(tr.select_one("td:nth-of-type(2) a"))
            title_map[title_lower] = has_link
    return title_map


# フェーズ1：API 全件取得 → comparison_new_title_with_links.html 作成
def fetch_all_and_write_temp():
    resp = requests.get(
        API_BASE,
        params=PARAMS,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer":    "https://animestore.docomo.ne.jp/animestore/CF/new_anime"
        },
        timeout=10
    )
    resp.raise_for_status()
    works = resp.json() if isinstance(resp.json(), list) else []

    temp_soup = BeautifulSoup(
        "<table>"
        "  <thead><tr>"
        "    <th>タイトル</th>"
        "    <th>dアニメ</th>"
        "    <th>U-NEXT</th>"
        "  </tr></thead>"
        "  <tbody></tbody>"
        "</table>",
        "html.parser"
    )
    tbody = temp_soup.tbody

    for item in works:
        title = (item.get("title") or "").strip()
        kana  = (item.get("kana")  or "").strip()
        raw   = item.get("link")
        link  = raw.get("href") if isinstance(raw, dict) else raw
        if not title or not link or not kana:
            continue

        href = link if link.startswith("http") else f"https://animestore.docomo.ne.jp{link}"
        tr   = temp_soup.new_tag("tr", id=safe_id(title), **{"data-kana": kana})

        # 1列目：タイトルのみ
        td1 = temp_soup.new_tag("td")
        a1  = temp_soup.new_tag(
            "a",
            **{"class": "title-link", "data-id": safe_id(title)}
        )
        a1.string = title
        td1.append(a1); tr.append(td1)

        # 2列目：dアニメリンク ◎
        td2 = temp_soup.new_tag("td", style="text-align:center;")
        a2  = temp_soup.new_tag("a", href=href, target="_blank")
        a2.string = "◎"
        td2.append(a2); tr.append(td2)

        # 3列目：U-NEXT ✖
        td3 = temp_soup.new_tag("td", style="text-align:center;")
        span= temp_soup.new_tag("span", **{"class":"no-link"})
        span.string = "✖"
        td3.append(span); tr.append(td3)

        tbody.append(tr)

    Path(TEMP_HTML).write_text(str(temp_soup), encoding="utf-8")
    print(f"→ 全件 {len(works)} 件を書き出し: {TEMP_HTML}")

# フェーズ2：既存タイトル除外＋リンク更新 → 五十音HTMLに反映

def distribute_new_only(existing_map: dict[str, bool]):
    temp_soup = BeautifulSoup(Path(TEMP_HTML).read_text("utf-8"), "html.parser")
    new_rows  = temp_soup.find("tbody").find_all("tr")

    for key, path in ROW_FILES.items():
        soup  = BeautifulSoup(Path(path).read_text("utf-8"), "html.parser")
        table = soup.select_one("table.mark02")
        tbody = table.find("tbody")
        if tbody is None:
            tbody = soup.new_tag("tbody")
            for tr in table.find_all("tr")[1:]:
                tbody.append(tr.extract())
            table.append(tbody)

        for tr in new_rows:
            title       = tr.select_one("a.title-link").text.strip()
            title_lower = title.lower()
            kana        = tr["data-kana"]
            href        = tr.select_one("td:nth-of-type(2) a")["href"]
            ini         = first_hiragana_from_kana(kana)
            ini_key     = INITIAL_MAP.get(ini, "10_wa")

            # 行キーが合わなければスキップ
            if ini_key != key:
                continue
            if title_lower in existing_map:
                # リンク未登録なら更新
                if not existing_map[title_lower]:
                    for etr in tbody.find_all("tr"):
                        if etr.select_one("a.title-link").text.strip().lower() == title_lower:
                            td2 = etr.select_one("td:nth-of-type(2)")
                            td2.clear()
                            new_a = soup.new_tag("a", href=href, target="_blank")
                            new_a.string = "◎"
                            td2.append(new_a)
                            break
                continue

            # 完全新規なら追加
            new_tr = BeautifulSoup(str(tr), "html.parser").find("tr")
            tbody.append(new_tr)

        Path(path).write_text(str(soup), encoding="utf-8")
        print(f" {path} に反映完了")


# 実行
if __name__ == "__main__":
    fetch_all_and_write_temp()
    existing = load_existing_titles()
    print(f"既存タイトル数: {len(existing)} 件")
    distribute_new_only(existing)
    print("全処理完了")
