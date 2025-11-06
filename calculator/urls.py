from django.urls import path
from . import views

app_name = 'calculator'

urlpatterns = [
    # http://ドメイン名/calculator/hello/
    # アドレス末尾と関数の紐づけ
    path('hello/', views.hello_view, name='hello'),

    # test動作用
    path('test/', views.test, name='test'),
    path('bmi/', views.bmi_view, name='bmi'),
    # def bmi_form(request):
    path('bmiform/', views.bmi_form, name='bmiform'),
    # def bmi_record_form(request):
    path('bmirecordform/', views.bmi_record_form, name='bmirecordform'),
    # def bmi_record_list(request):
    path('bmi_record_list/', views.bmi_record_list, name='bmi_record_list'),

    # def bmi_record_list_edit_delete(request): 編集・削除リンク付き一覧画面
    path('bmi_record_list_edit_delete/', views.bmi_record_list_edit_delete,
         name='bmi_record_list_edit_delete'),

    # BMIレコードの編集画面へのルート
    # <int:id> は対象レコードのIDをURLから取得するためのパラメータ
    path('bmi_record_edit/<int:id>/',
         views.bmi_record_edit, name='bmi_record_edit'),

    # BMIレコードの削除確認・処理画面へのルート
    # <int:id> は削除対象のレコードIDを指定
    path('bmi_record_delete/<int:id>/',
         views.bmi_record_delete, name='bmi_record_delete'),



]
