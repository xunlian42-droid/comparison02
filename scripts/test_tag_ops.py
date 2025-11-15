import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','conf.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
from comparison.models import Work,Tag,WorkTag
User=get_user_model()
user=User.objects.filter(is_superuser=True).first() or User.objects.first() or User.objects.create_user('tmp_tester','tmp@example.com','tmp_pass')
w, created_w = Work.objects.get_or_create(external_id='TEST_WORK_1', defaults={'title':'Test Work 1'})
t1, tc1 = Tag.objects.get_or_create(role='テスト', name='タグA', defaults={'created_by': user})
t2, tc2 = Tag.objects.get_or_create(role='テスト', name='タグB', defaults={'created_by': user})
wt1, wtc1 = WorkTag.objects.get_or_create(work=w, tag=t1, user=user)
wt2, wtc2 = WorkTag.objects.get_or_create(work=w, tag=t2, user=user)
print('WORK', w.id, w.title, 'created_w', created_w)
print('TAG1', t1.id, t1.role, t1.name, 'created', tc1, 'key', t1.key)
print('TAG2', t2.id, t2.role, t2.name, 'created', tc2, 'key', t2.key)
print('WT1', wtc1, 'WT2', wtc2)
qs = Work.objects.filter(work_tags__tag=t1).filter(work_tags__tag=t2).distinct()
print('works_with_both', list(qs.values_list('id','title')))
