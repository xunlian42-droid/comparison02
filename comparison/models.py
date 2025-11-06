from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Work(models.Model):
    title = models.CharField(max_length=255)
    external_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title

class Tag(models.Model):
    role = models.CharField(max_length=100, default="未設定")  # 例: 監督
    name = models.CharField(max_length=100, default="未設定")  # 例: 湯浅政明
    # works は WorkTag モデル経由でアクセス
    works = models.ManyToManyField(
        Work,
        through='WorkTag',
        through_fields=('tag', 'work'),
        related_name='tags'
    )
    key = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        blank=True,
        default=""
    )  # 正規化済み "監督:湯浅政明"
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # auto_now_add=Trueから変更
    # default=timezone.now

    def save(self, *args, **kwargs):
        # キーを自動生成（role:nameの形式）
        # 既定値や空文字の場合に role:name を採用する
        if not self.key or self.key == '未設定:未設定':
            self.key = f"{self.role}:{self.name}"
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('role', 'name')
        ordering = ['role', 'name']

    def __str__(self):
        return f"{self.role}: {self.name}"

class WorkTag(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='work_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='work_tags')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # タグ付けした人
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('work', 'tag', 'user')
        ordering = ['created_at']
