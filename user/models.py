from django.db import models

# userアプリケーション
# Create your models here.
# テーブルクラス
class User(models.Model):
    # 列名
    username = models.CharField(max_length=150)
    email = models.EmailField()

    def __str__(self):
        return self.username