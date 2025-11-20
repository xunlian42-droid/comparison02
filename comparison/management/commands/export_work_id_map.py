import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from comparison.models import Work

class Command(BaseCommand):
    help = 'Work テーブルから external_to_work_id.json を再生成する'

    def handle(self, *args, **kwargs):
        mapping = {}
        for work in Work.objects.all():
            mapping[work.external_id] = work.id

        output_path = os.path.join(settings.BASE_DIR, 'external_to_work_id.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(
            f'✅ external_to_work_id.json を再生成しました: {output_path} (件数: {len(mapping)})'
        ))
