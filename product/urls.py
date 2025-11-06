
from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    # test動作用
    path('test/', views.test, name='test'),
    # 商品登録
    # path('/', views., name=''),
    # 商品登録完了
    # path('thanks/', views.thanks, name='thanks'),

]
