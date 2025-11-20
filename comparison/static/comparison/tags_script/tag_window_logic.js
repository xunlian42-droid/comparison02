document.addEventListener("DOMContentLoaded", () => {
    (async () => {
        const hashId = decodeURIComponent(location.hash.slice(1));
        const allTags = document.getElementById("all-tags");
        const container = document.getElementById("tag-container");
        let currentId = null;

        // 1. 全ブロックをインデックス化
        const tagIndex = {};
        allTags.querySelectorAll("div[id]").forEach(div => {
            const workId = div.id;
            const title = div.querySelector("h3")?.textContent.trim() || workId;
            div.querySelectorAll("li").forEach(li => {
                const strong = li.querySelector("strong");
                if (!strong) return;
                const role = strong.textContent.replace(/[:：]\s*$/, "").trim();
                const name = li.textContent.replace(strong.textContent, "").trim();
                // キーは常に "役職: 名前"（コロンの後にスペース1個）で統一する
                const key = `${role}: ${name}`;
                if (!tagIndex[key]) {
                    tagIndex[key] = [];
                }
                // 重複を避けるために既存のエントリをチェック
                if (!tagIndex[key].some(entry => entry.id === workId)) {
                    tagIndex[key].push({ id: workId, title });
                }
            });
        });

        // 2. currentId を設定して表示処理を開始
        currentId = hashId;
        const blk = allTags.querySelector(`#${CSS.escape(hashId)}`);
        if (blk) {
            await showTagsFor(currentId);
        } else {
            try {
                const response = await fetch(`/comparison/api/work/${encodeURIComponent(hashId)}/tags/`);
                const data = await response.json();
                if (data.status === 'ok' && data.tags && data.tags.length > 0) {
                    await showTagsFor(currentId);
                } else {
                    showAddTagForMissing(hashId, container);
                }
            } catch (err) {
                console.warn('タグ取得エラー:', err);
                showAddTagForMissing(hashId, container);
            }
        }

        // ユーティリティ関数
        function splitOnce(str) {
            if (!str) return ['', ''];
            const idx = str.indexOf(':');
            if (idx === -1) return [str.trim(), ''];
            const left = str.slice(0, idx).trim();
            const right = str.slice(idx + 1).trim();
            return [left, right];
        }

        async function showTagsFor(workId) {
            const blk = allTags.querySelector(`#${CSS.escape(workId)}`);
            const container = document.getElementById('tag-container');
            if (!container) return;
            let title = workId;
            if (blk && blk.querySelector("h3")) {
                title = blk.querySelector("h3").textContent.trim();
            } else {
                try {
                    const res = await fetch(`/comparison/api/work/${encodeURIComponent(workId)}/info/`);
                    const info = await res.json();
                    if (info.title) {
                        title = info.title;
                    }
                } catch (err) {
                    console.warn('作品情報取得失敗:', err);
                }
            }

            // HTMLからタグを取得
            const htmlTags = [];
            if (blk) {
                blk.querySelectorAll("li").forEach(li => {
                    const strong = li.querySelector("strong");
                    if (!strong) return;
                    const role = strong.textContent.replace(/:$/, "").trim();
                    const name = li.textContent.replace(strong.textContent, "").trim();
                    const tag = `${role}: ${name}`;
                    htmlTags.push(tag);
                    // タグインデックスを更新
                    if (!tagIndex[tag]) {
                        tagIndex[tag] = [];
                    }
                    if (!tagIndex[tag].some(entry => entry.id === workId)) {
                        tagIndex[tag].push({ id: workId, title });
                    }
                });
            }

            // サーバーからタグ情報を取得して更新
            let serverTags = [];
            try {
                const response = await fetch(`/comparison/api/work/${encodeURIComponent(workId)}/tags/`);
                const data = await response.json();
                if (data.status === 'ok') {
                    if (data.tag_details) {
                        data.tag_details.forEach(tagDetail => {
                            const tagKey = tagDetail.tag;
                            if (!tagIndex[tagKey]) {
                                tagIndex[tagKey] = [];
                            }
                            tagDetail.related_works.forEach(work => {
                                if (!tagIndex[tagKey].some(entry => entry.id === work.external_id)) {
                                    tagIndex[tagKey].push({
                                        id: work.external_id,
                                        title: work.title
                                    });
                                }
                            });
                        });
                    }
                    if (data.tags) {
                        serverTags = data.tags;
                    }
                }
            } catch (err) {
                console.warn('タグ情報の取得に失敗:', err);
            }

            // HTMLとサーバーのタグを統合して重複を除去
            const uniqueTags = Array.from(new Set([...htmlTags, ...serverTags]));
            // 描画
            container.innerHTML = `<h3>${title}</h3>`;
            const tagList = document.createElement('div');
            tagList.id = 'tag-list';
            tagList.className = 'tag-list';

            uniqueTags.forEach(tag => {
                const span = document.createElement('span');
                span.className = 'tag-item';
                span.textContent = tag;
                span.addEventListener('click', () => showTagResults(tag, workId));
                tagList.appendChild(span);
            });

            container.appendChild(tagList);
            attachAddTagUI(container, workId);
        }


        // --- workPageMap を非同期で読み込む（1回だけ） ---
        window._workPageMapLoaded = window._workPageMapLoaded || (function () {
            window.workPageMap = window.workPageMap || {};
            const url = window.workPageMapUrl || '/static/comparison/workPageMap.json';
            return fetch(url, { cache: 'no-store' })
                .then(r => r.ok ? r.json() : Promise.reject(r.statusText))
                .then(j => { window.workPageMap = j; })
                .catch(e => {
                    console.warn('workPageMap load failed:', e);
                    window.workPageMap = {};
                });
        })();


        // --- ポップアップ側で親へ遷移/スクロールを指示するユーティリティ ---
        function openInParentAndGotoByInfo(pageInfo, fallbackKey) {
            const anchor = (pageInfo && pageInfo.anchor) ? pageInfo.anchor : fallbackKey;
            const encodedAnchor = encodeURIComponent(anchor);

            // --- workPageMap から比較表ファイル名を抽出 ---
            let pagePath = (pageInfo && pageInfo.page) ? pageInfo.page : '';
            if (!pagePath && fallbackKey && window.workPageMap && window.workPageMap[fallbackKey]) {
                pagePath = window.workPageMap[fallbackKey].page || '';
            }
            let filename = pagePath.split('/').pop(); // → comparison_10_wa_with_links.html

            // DjangoのURLに変換
            let targetPage = filename ? `/comparison/comparison/${filename}` : (window.currentPageFilename ? window.currentPageFilename() : '');


            // source_external_id を付加（タグページが誰から開かれたかを知るため）
            const sourceParam = fallbackKey ? `?source_external_id=${encodeURIComponent(fallbackKey)}` : '';
            const absoluteUrl = `${window.location.origin}${targetPage}${sourceParam}#${encodedAnchor}`;

            const openerExists = window.opener && !window.opener.closed;
            if (!openerExists) {
                window.location.href = absoluteUrl;
                return;
            }

            try {
                const openerHref = window.opener.location.href;
                const openerPage = (new URL(openerHref)).pathname.split('/').pop();

                if (openerPage === targetPage.split('/').pop()) {
                    // 同じページなら postMessage でスクロール
                    window.opener.postMessage({ action: 'goto', anchor }, window.location.origin);
                    window.close();
                    return;
                }

                // 別ページなら親を遷移させる
                else {
                    window.opener.postMessage({ action: 'navigate', url: absoluteUrl }, window.location.origin);
                }

                window.close();
            } catch (err) {
                try {
                    window.opener.location.href = absoluteUrl;
                } catch (e) {
                    window.location.href = absoluteUrl;
                } finally {
                    window.close();
                }
            }
        }

        function showTagResults(tagKey, workId) {
            console.log('タグ検索:', tagKey, tagIndex[tagKey]); // デバッグログ
            const entries = tagIndex[tagKey] || [];
            container.innerHTML = '';

            if (!entries.length) {
                container.innerHTML = `<p>タグ「${tagKey}」を持つ作品は見つかりません。</p>`;
                return;
            }

            container.innerHTML = `<h4>タグ「${tagKey}」を持つ作品</h4>`;
            const ul = document.createElement("ul");

            entries.forEach(({ id, title }) => {
                const li = document.createElement("li");
                const a = document.createElement("a");
                a.textContent = title;
                // a.href = "#";

                // workPageMapからページ情報を取得してアンカー付きURLを生成
                const pageInfo = window.workPageMap?.[id] || null;
                const anchor = id;
                const encodedAnchor = encodeURIComponent(anchor);
                const pagePath = pageInfo?.page || '';
                const filename = pagePath.split('/').pop();
                const targetPage = filename ? `/comparison/comparison/${filename}` : '';
                a.href = `${targetPage}#${encodedAnchor}`;


                a.addEventListener("click", e => {
                    e.preventDefault();

                    window._workPageMapLoaded.then(() => {
                        const key = id;
                        const pageInfo = window.workPageMap?.[key] || null;

                        if (window.opener) {
                            openInParentAndGotoByInfo(pageInfo, key);
                        } else {
                            const anchor = key;
                            const encodedAnchor = encodeURIComponent(anchor);
                            const pagePath = pageInfo?.page || '';
                            const filename = pagePath.split('/').pop();
                            const targetPage = filename ? `/comparison/${filename}` : '';
                            const absoluteUrl = `${window.location.origin}${targetPage}#${encodedAnchor}`;
                            window.location.href = absoluteUrl;
                        }
                    }).catch(() => {
                        const anchor = id;
                        if (window.opener?.scrollToTitle) {
                            window.opener.scrollToTitle(anchor);
                            window.close();
                        } else {
                            window.location.href = `#${encodeURIComponent(anchor)}`;
                        }
                    });
                });

                li.appendChild(a);
                ul.appendChild(li);
            });


            container.appendChild(ul);

            const back = document.createElement("a");
            back.href = "#";
            back.textContent = "← タグ一覧に戻る";
            back.className = "back-to-tags";
            back.addEventListener("click", e => {
                e.preventDefault();
                if (workId) {
                    showTagsFor(workId);
                } else {
                    container.innerHTML = '<p>タグ一覧に戻れませんでした。</p>';
                }
            });

            container.appendChild(back);
        }

        function getCookie(name) {
            const v = document.cookie.split('; ').find(row => row.startsWith(name + '='));
            return v ? decodeURIComponent(v.split('=')[1]) : null;
        }

        function attachAddTagUI(container, workId) {
            if (container.querySelector('#add-tag-form')) return;

            const form = document.createElement('form');
            form.id = 'add-tag-form';
            form.innerHTML = `
                <input type="text" id="add-tag-input" name="tag" placeholder="新しいタグを入力" maxlength="100" required />
                <button type="submit">タグを追加</button>
                <div id="add-tag-msg" aria-live="polite" style="margin-top:8px"></div>
            `;
            container.appendChild(form);

            form.addEventListener('submit', async function (e) {
                e.preventDefault();
                const input = form.querySelector('#add-tag-input');
                const tag = input.value.trim();
                if (!tag) return;

                const csrftoken = getCookie('csrftoken');
                const url = `/comparison/api/work/${encodeURIComponent(workId)}/add_tag/`;
                try {
                    const resp = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrftoken,
                            'Accept': 'application/json',
                            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
                        },
                        body: new URLSearchParams({ tag })
                    });

                    if (resp.status === 302 || resp.status === 401 || resp.status === 403) {
                        let errMsg = '未ログインです。ログインしてください。';
                        try {
                            const j = await resp.json();
                            if (j && (j.message || j.error)) errMsg = j.message || j.error;
                        } catch (e) { }
                        form.querySelector('#add-tag-msg').textContent = errMsg;

                        const loginLink = document.createElement('a');
                        loginLink.href = '/accounts/login/?next=' + encodeURIComponent(location.pathname + location.search);
                        loginLink.textContent = 'ログインする';
                        loginLink.style.display = 'block';
                        form.appendChild(loginLink);
                        return;
                    }

                    if (!resp.ok) {
                        let txt = resp.statusText;
                        try {
                            const j = await resp.json();
                            txt = j.message || j.error || JSON.stringify(j);
                        } catch (e) {
                            txt = await resp.text().catch(() => resp.statusText);
                        }
                        throw new Error(txt || 'サーバエラー');
                    }

                    const data = await resp.json();
                    form.querySelector('#add-tag-msg').textContent = `タグ「${data.tag}」を追加しました`;
                    input.value = '';
                    await showTagsFor(workId);

                } catch (err) {
                    form.querySelector('#add-tag-msg').textContent = `追加に失敗しました: ${err.message}`;
                }
            });
        }

        function showMessage(container, msg, isError = false) {
            let el = container.querySelector('.ajax-msg');
            if (!el) {
                el = document.createElement('div');
                el.className = 'ajax-msg';
                container.appendChild(el);
            }
            el.textContent = msg;
            el.style.color = isError ? 'crimson' : 'green';
        }

        function showAddTagForMissing(workId, container) {
            container.innerHTML = `<h3>${workId}</h3>`;
            const p = document.createElement('p');
            p.textContent = 'タグ情報が見つかりません。新しくタグを追加できます。';
            container.appendChild(p);

            const form = document.createElement('form');
            form.id = 'add-tag-form-missing';
            form.innerHTML = `
                <input type="text" id="add-tag-input-missing" name="tag" placeholder="新しいタグを入力" maxlength="100" required />
                <input type="hidden" id="add-title-input-missing" name="title" value="${workId}" />
                <button type="submit">タグを追加</button>
            `;
            container.appendChild(form);

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const tag = form.querySelector('#add-tag-input-missing').value.trim();
                const title = form.querySelector('#add-title-input-missing').value.trim();
                if (!tag) {
                    showMessage(container, 'タグ名を入力してください', true);
                    return;
                }

                const csrftoken = getCookie('csrftoken');
                const url = `/comparison/api/work/${encodeURIComponent(workId)}/add_tag/`;
                try {
                    const resp = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrftoken,
                            'Accept': 'application/json',
                            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
                        },
                        body: new URLSearchParams({ tag, title })
                    });

                    if (resp.status === 302 || resp.status === 401 || resp.status === 403) {
                        let errMsg = '未ログインです。ログインしてください。';
                        try {
                            const j = await resp.json();
                            if (j && (j.message || j.error)) errMsg = j.message || j.error;
                        } catch (e) { }
                        showMessage(container, errMsg, true);

                        const link = document.createElement('a');
                        link.href = '/accounts/login/?next=' + encodeURIComponent(location.pathname + location.search);
                        link.textContent = 'ログインしてタグを追加する';
                        link.style.display = 'block';
                        container.appendChild(link);
                        return;
                    }

                    if (!resp.ok) {
                        let txt = resp.statusText;
                        try {
                            const j = await resp.json();
                            txt = j.message || j.error || JSON.stringify(j);
                        } catch (e) {
                            txt = await resp.text().catch(() => resp.statusText);
                        }
                        showMessage(container, `追加に失敗しました: ${txt || resp.statusText}`, true);
                        return;
                    }

                    const data = await resp.json();
                    await showTagsFor(workId);
                    showMessage(container, `タグ「${data.tag}」を追加しました`);

                } catch (err) {
                    showMessage(container, `通信エラー: ${err.message}`, true);
                }
            });
        }
    })();
});