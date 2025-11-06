(() => {
    const rowKey = window.rowKey || "ka"; // ページごとの行キー（例: "a", "ka", ...）

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll("a.title-link").forEach(a => {
            a.addEventListener("click", e => {
                e.preventDefault();
                const id = a.dataset.id;
                if (!id) return;

                // タグウインドウのURL（アンカーで作品IDを渡す）
                const tagWindowURL = `/comparison/tags_html_folder/02_${rowKey}_tags_processed/#${encodeURIComponent(id)}`;

                // 別ウインドウを開く
                window.open(
                    tagWindowURL,
                    "tagWindow",
                    "width=700,height=800,scrollbars=yes,resizable=yes"
                );
            });
        });
    });

    // 比較表ページに作品IDでスクロールする関数（タグウインドウから呼ばれる）
    window.scrollToTitle = function (id) {
        const target = document.getElementById(id);
        if (target) {
            target.scrollIntoView({ behavior: "smooth", block: "center" });
            target.classList.add("highlight");
            setTimeout(() => target.classList.remove("highlight"), 10000);
        }
    };

    // 親側: ポップアップからの指示を受けてスクロールする
    window.addEventListener('message', (ev) => {
        if (!ev.data || ev.data.action !== 'goto') return;
        const anchor = ev.data.anchor;
        if (!anchor) return;

        // 履歴に残す
        try { location.hash = '#' + anchor; } catch (e) {}

        const el = document.getElementById(anchor);
        if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            el.classList.add('highlight');
            setTimeout(() => el.classList.remove('highlight'), 3000);
            return;
        }

        // 要素がまだ無ければポーリング
        let tries = 0;
        const t = setInterval(() => {
            const e2 = document.getElementById(anchor);
            tries++;
            if (e2) {
                clearInterval(t);
                e2.scrollIntoView({ behavior: 'smooth', block: 'center' });
                e2.classList.add('highlight');
                setTimeout(() => e2.classList.remove('highlight'), 3000);
            } else if (tries > 25) {
                clearInterval(t);
            }
        }, 200);
    });
})();
