from django import forms
from django.db import models

# Create your models here.

# BMI用のレコードを格納するテーブルクラス


class BmiRecord(models.Model):
    simei = models.CharField(
        verbose_name='お名前',
        max_length=50
    )
    height = models.FloatField(
        verbose_name='身長(cm)',
    )
    weight = models.FloatField(
        verbose_name='体重(kg)',
    )

    def __str__(self):
        return f"{self.simei} - {self.height}cm / {self.weight}kg"

    def bmi(self):
        """BMI値を計算して返す（身長はcmからmに変換）"""
        if self.height > 0:
            return round(self.weight / ((self.height / 100) ** 2), 2)
        return None
