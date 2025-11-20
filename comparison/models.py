from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Work(models.Model):
    title = models.CharField(max_length=255)
    external_id = models.CharField(max_length=100, unique=True)

    comparison_page = models.CharField(
        max_length=20, blank=True, null=True, help_text="比較表ファイル名の識別子（例: '01_a'）")
    id_for_anchor = models.CharField(max_length=100, blank=True, null=True, help_text="比較表HTML内のアンカーID（例: '11eyes'）")

    def __str__(self):
        return self.title
    
    def get_comparison_url(self):
        if self.comparison_page and self.id_for_anchor:
            return f"/comparison/comparison_gojuon_with_links/comparison_{self.comparison_page}_with_links/#{self.id_for_anchor}"
        elif self.comparison_page:
            return f"/comparison/comparison_gojuon_with_links/comparison_{self.comparison_page}_with_links/"
        return None


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
        # keyフィールドをroleとnameの組み合わせで設定
        self.key = f"{self.role}:{self.name}".strip()

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
    can_edit = models.BooleanField(default=True)  # 自分が追加した作品タグは編集可能

    class Meta:
        unique_together = ('work', 'tag', 'user')
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username} tagged '{self.work.title}' with '{self.tag.key}'"



class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'work')  # 同じ作品を複数回お気に入りできないように


from django.conf import settings


class MyList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # リスト名（例：視聴して面白かった作品）
    description = models.TextField(blank=True)  # 任意の説明
    is_public = models.BooleanField(default=False)  # 公開/非公開設定
    created_at = models.DateTimeField(auto_now_add=True)

class MyListItem(models.Model):
    mylist = models.ForeignKey(MyList, on_delete=models.CASCADE, related_name="items")
    work = models.ForeignKey(Work, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
