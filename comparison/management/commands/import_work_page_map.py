import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from comparison.models import Work

class Command(BaseCommand):
    help = 'workPageMap.json を使って Work モデルに comparison_page と id_for_anchor を登録する'

    def handle(self, *args, **kwargs):
        # プロジェクトルートからの絶対パス
        json_path = os.path.join(settings.BASE_DIR, 'workPageMap.json')

        if not os.path.exists(json_path):
            self.stderr.write(self.style.ERROR(f'❌ JSONファイルが見つかりません: {json_path}'))
            return

        try:
            with open(json_path, encoding='utf-8') as f:
                page_map = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ JSON読み込みエラー: {e}'))
            return

        updated = 0
        skipped = 0

        for ext_id, info in page_map.items():
            try:
                work = Work.objects.get(external_id=ext_id)
                action = "更新"

                # ファイル名から比較表識別子を抽出
                filename = os.path.basename(info.get('page', ''))
                page_part = filename.replace('comparison_', '').replace('_with_links.html', '')

                # 表示用タイトルがあれば設定（既存タイトルが空の場合や明示的に上書きしたい場合）
                title = info.get('title') or info.get('raw') or ext_id

                work.comparison_page = page_part
                work.id_for_anchor = info.get('anchor', ext_id)
                if not getattr(work, 'title', None):
                    work.title = title
                work.save()

                updated += 1
                self.stdout.write(f'✅ {action}: {ext_id} → title={work.title}, page={page_part}, anchor={work.id_for_anchor}')

            except Work.DoesNotExist:
                # 新規作成
                try:
                    filename = os.path.basename(info.get('page', ''))
                    page_part = filename.replace('comparison_', '').replace('_with_links.html', '')
                    title = info.get('title') or info.get('raw') or ext_id

                    work = Work(
                        external_id=ext_id,
                        title=title,
                        comparison_page=page_part,
                        id_for_anchor=info.get('anchor', ext_id)
                    )
                    work.save()
                    updated += 1
                    self.stdout.write(f'✅ 新規作成: {ext_id} → title={work.title}, page={page_part}, anchor={work.id_for_anchor}')
                except Exception as e:
                    skipped += 1
                    self.stderr.write(self.style.ERROR(f'❌ 作成失敗: {ext_id}: {e}'))
            except Exception as e:
                skipped += 1
                self.stderr.write(self.style.ERROR(f'❌ エラー: {ext_id}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'完了: {updated} 件登録, {skipped} 件スキップ'))