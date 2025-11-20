const pageList = [
  { href: "/comparison/comparison_gojuon_with_links/comparison_01_a_with_links/" },
  { href: "/comparison/comparison_gojuon_with_links/comparison_02_ka_with_links/" },
  { href: "/comparison/comparison_gojuon_with_links/comparison_03_sa_with_links/" },
  { href: "/comparison/comparison_gojuon_with_links/comparison_04_ta_with_links/" },
  { href: "/comparison/comparison_gojuon_with_links/comparison_05_na_with_links/" },
  { href: "/comparison/comparison_gojuon_with_links/comparison_06_ha_with_links/" },
  { href: "/comparison/comparison_gojuon_with_links/comparison_07_ma_with_links/" },
  { href: "/comparison/comparison_gojuon_with_links/comparison_08_ya_with_links/" },
  { href: "/comparison/comparison_gojuon_with_links/comparison_09_ra_with_links/" },
  { href: "/comparison/comparison_gojuon_with_links/comparison_10_wa_with_links/" }
];

let titleIndex = [];

function generateAnchorId(title) {
  // タイトルからアンカーIDを生成
  return title
    .replace(/[^\p{L}\p{N}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Han}_]/gu, "_");
}

async function buildTitleIndex() {
  titleIndex = [];
  for (const page of pageList) {
    try {
      const res = await fetch(page.href);
      if (!res.ok) continue;
      const html = await res.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");

      // タイトルリンクだけを対象にする
      doc.querySelectorAll("tbody tr td").forEach(tr => {
        const title = tr.textContent.trim();
        if (title) {
          const anchor = generateAnchorId(title);
          titleIndex.push({
            title: title,
            page: page.href,
            anchor: anchor,
            id: anchor
          });
        }
      });

    } catch (e) {
      console.warn("読み込み失敗:", page.href);
    }
  }
}

// タイトル検索用インデックス
async function doSearch() {
  const query = document.getElementById('search-input').value.trim();
  const exclude = document.getElementById('exclude-input').value.trim();
  const words = query ? query.split(/\s+/) : [];
  const excludes = exclude ? exclude.split(/\s+/) : [];

  if (titleIndex.length === 0) {
    document.getElementById('result-count').textContent = "検索中...";
    await buildTitleIndex();
  }

  const results = titleIndex.filter(item => {
    const match = words.every(w => item.title.includes(w));
    const notExcluded = excludes.every(w => !item.title.includes(w));
    return match && notExcluded;
  });


  const ul = document.getElementById('result-list');
  ul.innerHTML = '';
  results.forEach(item => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = `${item.page}#${item.id}`;
    a.target = "_blank";
    a.textContent = item.title;

    a.addEventListener("click", e => {
      e.preventDefault();
      sessionStorage.setItem("scrollToId", item.id);
      window.open(a.href, '_blank');
    });

    li.appendChild(a);
    ul.appendChild(li);
  });


  document.getElementById('result-count').textContent = `${results.length}件ヒット`;
}





document.getElementById('search-form').addEventListener('submit', doSearch);

document.getElementById('reset-btn').addEventListener('click', function () {
  document.getElementById('search-input').value = '';
  document.getElementById('exclude-input').value = '';
  document.getElementById('result-count').textContent = '';
  const ul = document.getElementById('result-list');
  ul.innerHTML = `
    <li><a href="/comparison/comparison_gojuon_with_links/comparison_01_a_with_links/">ア行の作品比較</a></li>
    <li><a href="/comparison/comparison_gojuon_with_links/comparison_02_ka_with_links/">カ行の作品比較</a></li>
    <li><a href="/comparison/comparison_gojuon_with_links/comparison_03_sa_with_links/">サ行の作品比較</a></li>
    <li><a href="/comparison/comparison_gojuon_with_links/comparison_04_ta_with_links/">タ行の作品比較</a></li>
    <li><a href="/comparison/comparison_gojuon_with_links/comparison_05_na_with_links/">ナ行の作品比較</a></li>
    <li><a href="/comparison/comparison_gojuon_with_links/comparison_06_ha_with_links/">ハ行の作品比較</a></li>
    <li><a href="/comparison/comparison_gojuon_with_links/comparison_07_ma_with_links/">マ行の作品比較</a></li>
    <li><a href="/comparison/comparison_gojuon_with_links/comparison_08_ya_with_links/">ヤ行の作品比較</a></li>
    <li><a href="/comparison/comparison_gojuon_with_links/comparison_09_ra_with_links/">ラ行の作品比較</a></li>
    <li><a href="/comparison/comparison_gojuon_with_links/comparison_10_wa_with_links/">ワ行の作品比較</a></li>
  `;
});



// タグ検索用インデックス

const tagIndex = {}; // { "役職:名前": [ { id, title, rowKey } ] }

async function buildTagIndex() {
  const res = await fetch(ALL_TAGS_URL);
  const html = await res.text();
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");

  doc.querySelectorAll("#all-tags > div[id]").forEach(div => {
    const workId = div.id;
    const rowKey = div.dataset.row;
    const title = div.querySelector("h3")?.textContent.trim() || workId;

    div.querySelectorAll("li").forEach(li => {
      const strong = li.querySelector("strong");
      if (!strong) return;
      const role = strong.textContent.replace(/:$/, "");
      const name = li.textContent.replace(strong.textContent, "").trim();
      const key = `${role}:${name}`;
      (tagIndex[key] = tagIndex[key] || []).push({ id: workId, title, rowKey });
    });
  });
}

async function doTagSearch() {
  const query = document.getElementById("tag-input").value.trim();
  const excludeQuery = document.getElementById("tag-exclude-input").value.trim();

  const keywords = query ? query.split(/\s+/).map(w => w.replace(/\s+/g, "")) : [];
  const excludeKeywords = excludeQuery ? excludeQuery.split(/\s+/).map(w => w.replace(/\s+/g, "")) : [];


  if (Object.keys(tagIndex).length === 0) {
    document.getElementById("tag-result-count").textContent = "タグ読み込み中...";
    await buildTagIndex();
  }

  const workMap = new Map(); // Map<workId, { id, title, rowKey, tagKeys[] }>

  // タグインデックスから作品ごとにタグを集約
  Object.entries(tagIndex).forEach(([tagKey, entries]) => {
    const normalizedKey = tagKey.replace(/\s+/g, "");
    entries.forEach(({ id, title, rowKey }) => {
      if (!workMap.has(id)) {
        workMap.set(id, { id, title, rowKey, tagKeys: [] });
      }
      workMap.get(id).tagKeys.push(normalizedKey);
    });
  });

  const results = [];

  // 作品ごとに検索語と除外語を判定
  for (const work of workMap.values()) {
    const hasAnyTag = keywords.some(word =>
      work.tagKeys.some(tag => tag.includes(word))
    );
    const hasExclude = excludeKeywords.some(word =>
      work.tagKeys.some(tag => tag.includes(word))
    );
    if (hasAnyTag && !hasExclude) {
      results.push(work);
    }
  }


  // 結果表示
  const ul = document.getElementById("tag-result-list");
  ul.innerHTML = "";
  results.forEach(({ id, title, rowKey }) => {
    const li = document.createElement("li");
    const a = document.createElement("a");
    const pageHref = `/comparison/comparison_gojuon_with_links/comparison_${getRowNumber(rowKey)}_${rowKey}_with_links/`;
    a.href = `${pageHref}#${id}`;
    a.textContent = `${title}`;
    a.addEventListener("click", () => {
      sessionStorage.setItem("scrollToId", id);
    });
    li.appendChild(a);
    ul.appendChild(li);
  });


  document.getElementById("tag-result-count").textContent = `${results.length}件ヒット`;
}

// タグ入力補完
document.getElementById("tag-input").addEventListener("input", () => {
  const input = document.getElementById("tag-input").value.trim().replace(/\s+/g, "");
  const suggestionBox = document.getElementById("tag-suggestions");
  suggestionBox.innerHTML = "";

  if (!input || Object.keys(tagIndex).length === 0) return;

  const matches = Object.keys(tagIndex).filter(tagKey =>
    tagKey.replace(/\s+/g, "").includes(input)
  ).slice(0, 10); // 最大10件表示

  matches.forEach(tagKey => {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = "#";
    a.textContent = tagKey;
    a.addEventListener("click", e => {
      e.preventDefault();
      document.getElementById("tag-input").value = tagKey;
      suggestionBox.innerHTML = "";
    });
    li.appendChild(a);
    suggestionBox.appendChild(li);
  });
});


document.getElementById("tag-search-form").addEventListener("submit", async (e) => {
  e.preventDefault(); // ページ遷移を防ぐ
  await doTagSearch(); // 検索処理を呼び出す
});

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("tag-reset-btn").addEventListener("click", () => {
    // フォーム全体をリセット
    document.getElementById("tag-search-form").reset();

    // 検索結果や候補もクリア
    document.getElementById("tag-suggestions").innerHTML = "";
    document.getElementById("tag-result-count").textContent = "";
    document.getElementById("tag-result-list").innerHTML = "";
  });
});


document.addEventListener("DOMContentLoaded", async () => {
  await buildTagIndex(); // タグインデックスを事前構築
});


// タグポップアップを開く関数

document.getElementById('openTagPopup').addEventListener('click', () => {
  const url = document.getElementById('openTagPopup').dataset.url;
  window.open(
    url,
    'tagPopupWindow',
    'width=600,height=700,resizable=yes,scrollbars=yes'
  );
});



// タグポップアップから呼ばれる関数
window.showTagResults = function (tagKey, entries) {
  const ul = document.getElementById("tag-result-list");
  ul.innerHTML = "";

  entries.forEach(({ id, title, rowKey }) => {
    const li = document.createElement("li");
    const a = document.createElement("a");

    const pageHref = `/comparison/comparison_gojuon_with_links/comparison_${getRowNumber(rowKey)}_${rowKey}_with_links/`;
    a.href = `${pageHref}#${id}`;

    a.textContent = `${title}`;
    a.addEventListener("click", () => {
      sessionStorage.setItem("scrollToId", id);
    });
    li.appendChild(a);
    ul.appendChild(li);
  });

  document.getElementById("tag-result-count").textContent = `タグ「${tagKey}」に一致する作品：${entries.length}件`;
};

function getRowNumber(rowKey) {
  const map = {
    "a": "01", "ka": "02", "sa": "03", "ta": "04", "na": "05",
    "ha": "06", "ma": "07", "ya": "08", "ra": "09", "wa": "10"
  };
  return map[rowKey] || "00";
}

