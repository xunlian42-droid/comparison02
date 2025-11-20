(() => {
    const rowKey = window.rowKey || "ma"; // ページごとの行キー（例: "a", "ka", ...）

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll("a.title-link").forEach(a => {
            a.addEventListener("click", e => {
                e.preventDefault();
                const id = a.dataset.id;
                if (!id) return;

                // タグウインドウのURL（アンカーで作品IDを渡す）
                const tagWindowURL = `/comparison/tags_html_folder/07_${rowKey}_tags_processed/#${encodeURIComponent(id)}`;

                // 別ウインドウを開く
                window.open(
                    tagWindowURL,
                    "tagWindow",
                    "width=700,height=800,scrollbars=yes,resizable=yes"
                );
            });
        });
    });
})();



(function(){
  // CSRFトークン取得（cookieから）
  function getCookie(name){
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? decodeURIComponent(m.pop()) : null;
  }
  const csrftoken = getCookie('csrftoken');

  // お気に入り追加／削除
  async function toggleFavorite(workId, btn){
    try {
      const isFav = btn.dataset.favorited === '1';
      const url = isFav
        ? `/comparison/favorite/remove/${workId}/`
        : `/comparison/favorite/add/${workId}/`;

      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'Accept': 'application/json'
        },
        credentials: 'same-origin'
      });

      const json = await res.json().catch(() => null);
      if (!json || json.status !== 'ok') {
        // UIは更新しないが、catchには落とさない
        console.warn('favorite toggle failed', json);
        alert(json?.message || '操作に失敗しました。ログイン状態やネットワークを確認してください。');
        return;
      }

      // UI更新
      btn.dataset.favorited = isFav ? '0' : '1';
      btn.textContent = isFav ? '☆' : '★';
      btn.title = isFav ? 'お気に入りに追加' : 'お気に入り解除';
    } catch (err) {
      console.warn('favorite toggle failed', err);
      alert('操作に失敗しました。ログイン状態やネットワークを確認してください。');
    }
  }

  // 初期状態取得（お気に入り済み作品の workId 一覧）
  let favoriteExternalIds = [];
  fetch('/comparison/api/my-favorites/', {
    headers: { 'Accept': 'application/json' },
    credentials: 'same-origin'
  })
  .then(res => res.ok ? res.json() : null)
  .then(json => {
    // お気に入り外部ID一覧を取得
    if (json && Array.isArray(json.external_ids)) {
      favoriteExternalIds = json.external_ids;
    }

    document.querySelectorAll('tr').forEach(tr => {
      const link = tr.querySelector('.title-link[data-id]');
      if (!link) return;

      const extId = link.dataset.id;
      const workId = link.dataset.workId; // 登録・解除用に使う
      const favCell = tr.querySelector('.fav-cell') || (function(){
        const td = document.createElement('td');
        td.className = 'fav-cell';
        tr.insertBefore(td, tr.firstChild);
        return td;
      })();

      const isFav = favoriteExternalIds.includes(extId);
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.dataset.favorited = isFav ? '1' : '0';
      btn.textContent = isFav ? '★' : '☆';
      btn.title = isFav ? 'お気に入り解除' : 'お気に入りに追加';

      btn.addEventListener('click', () => toggleFavorite(workId, btn));
      favCell.innerHTML = '';
      favCell.appendChild(btn);
    });
  });
})();

  