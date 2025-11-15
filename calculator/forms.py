from django import forms
from .models import BmiRecord

# 氏名のinputタグを生成するクラス
# 送信データを格納するクラスも兼ねる
class ProfileForm(forms.Form):
    simei = forms.CharField(label='お名前')

# BMI計算フォーム


class BmiForm(forms.Form):
    simei = forms.CharField(
        label='お名前',
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '例: 山田 太郎'
        })
    )
    height = forms.FloatField(
        label='身長(cm)',
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'step': '0.1',
            'placeholder': '例: 170.5'
        })
    )
    weight = forms.FloatField(
        label='体重(kg)',
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'step': '0.1',
            'placeholder': '例: 65.2'
        })
    )

# BmiRecordモデルに対応するModelFormクラスを定義


class BmiRecordForm(forms.ModelForm):
    # Metaクラスでフォームの設定を定義
    class Meta:
        # 対象となるモデルを指定
        model = BmiRecord
        # フォームに含めるフィールドを指定
        fields = ['simei', 'height', 'weight']
        # 各フィールドのラベル（表示名）を日本語で指定
        labels = {
            'simei': 'お名前',         # simeiフィールドのラベルを「お名前」に設定
            'height': '身長(cm)',      # heightフィールドのラベルを「身長(cm)」に設定
            'weight': '体重(kg)',      # weightフィールドのラベルを「体重(kg)」に設定
        }
        # 各フィールドの入力ウィジェット（HTMLの入力要素）をカスタマイズ
        widgets = {
            'simei': forms.TextInput(attrs={
                'placeholder': '例: 山田 太郎'  # simeiフィールドのプレースホルダーを設定
            }),
            'height': forms.NumberInput(attrs={
                'step': '0.1',                 # 小数点第1位まで入力可能にするステップ指定
                'placeholder': '例: 170.5'     # heightフィールドのプレースホルダーを設定
            }),
            'weight': forms.NumberInput(attrs={
                'step': '0.1',                 # 小数点第1位まで入力可能にするステップ指定
                'placeholder': '例: 65.2'      # weightフィールドのプレースホルダーを設定
            }),
        }
