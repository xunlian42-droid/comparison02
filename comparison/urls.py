from django.urls import path, include
from . import views
from django.shortcuts import render

from .views import AddTagView


app_name = 'comparison'

urlpatterns = [
    # index動作用
    path('', views.index, name='index'),
    # tag_popup
    path('tag_popup/', views.tag_popup, name='tag_popup'),
    # comparison_gojuon_with_links
    path('comparison_gojuon_with_links/comparison_01_a_with_links/', lambda r: render(r, 'comparison/comparison_gojuon_with_links/comparison_01_a_with_links.html'), name='01_a'),
    path('comparison_gojuon_with_links/comparison_02_ka_with_links/', lambda r: render(r, 'comparison/comparison_gojuon_with_links/comparison_02_ka_with_links.html'), name='02_ka'),
    path('comparison_gojuon_with_links/comparison_03_sa_with_links/', lambda r: render(r, 'comparison/comparison_gojuon_with_links/comparison_03_sa_with_links.html'), name='03_sa'),
    path('comparison_gojuon_with_links/comparison_04_ta_with_links/', lambda r: render(r, 'comparison/comparison_gojuon_with_links/comparison_04_ta_with_links.html'), name='04_ta'),
    path('comparison_gojuon_with_links/comparison_05_na_with_links/', lambda r: render(r, 'comparison/comparison_gojuon_with_links/comparison_05_na_with_links.html'), name='05_na'),
    path('comparison_gojuon_with_links/comparison_06_ha_with_links/', lambda r: render(r, 'comparison/comparison_gojuon_with_links/comparison_06_ha_with_links.html'), name='06_ha'),
    path('comparison_gojuon_with_links/comparison_07_ma_with_links/', lambda r: render(r, 'comparison/comparison_gojuon_with_links/comparison_07_ma_with_links.html'), name='07_ma'),
    path('comparison_gojuon_with_links/comparison_08_ya_with_links/', lambda r: render(r, 'comparison/comparison_gojuon_with_links/comparison_08_ya_with_links.html'), name='08_ya'),
    path('comparison_gojuon_with_links/comparison_09_ra_with_links/', lambda r: render(r, 'comparison/comparison_gojuon_with_links/comparison_09_ra_with_links.html'), name='09_ra'),
    path('comparison_gojuon_with_links/comparison_10_wa_with_links/', lambda r: render(r, 'comparison/comparison_gojuon_with_links/comparison_10_wa_with_links.html'), name='10_wa'),
    # tags_html_folder
    path('tags_html_folder/01_a_tags_processed/', lambda r: render(r, 'comparison/tags_html_folder/01_a_tags_processed.html'), name='01_a_tags'),
    path('tags_html_folder/02_ka_tags_processed/', lambda r: render(r, 'comparison/tags_html_folder/02_ka_tags_processed.html'), name='02_ka_tags'),
    path('tags_html_folder/03_sa_tags_processed/', lambda r: render(r, 'comparison/tags_html_folder/03_sa_tags_processed.html'), name='03_sa_tags'),
    path('tags_html_folder/04_ta_tags_processed/', lambda r: render(r, 'comparison/tags_html_folder/04_ta_tags_processed.html'), name='04_ta_tags'),
    path('tags_html_folder/05_na_tags_processed/', lambda r: render(r, 'comparison/tags_html_folder/05_na_tags_processed.html'), name='05_na_tags'),
    path('tags_html_folder/06_ha_tags_processed/', lambda r: render(r, 'comparison/tags_html_folder/06_ha_tags_processed.html'), name='06_ha_tags'),
    path('tags_html_folder/07_ma_tags_processed/', lambda r: render(r, 'comparison/tags_html_folder/07_ma_tags_processed.html'), name='07_ma_tags'),
    path('tags_html_folder/08_ya_tags_processed/', lambda r: render(r, 'comparison/tags_html_folder/08_ya_tags_processed.html'), name='08_ya_tags'),
    path('tags_html_folder/09_ra_tags_processed/', lambda r: render(r, 'comparison/tags_html_folder/09_ra_tags_processed.html'), name='09_ra_tags'),
    path('tags_html_folder/10_wa_tags_processed/', lambda r: render(r, 'comparison/tags_html_folder/10_wa_tags_processed.html'), name='10_wa_tags'),
    path('tags_html_folder/all_tags_combined/', lambda r: render(r, 'comparison/tags_html_folder/all_tags_combined.html'), name='all_tags'),
    
    # ユーザ登録
    path('register/', views.register, name='register'),


    # マイページ
    path('mypage/', views.mypage, name='mypage'),

    path('accounts/', include('django.contrib.auth.urls')),

    path('api/work/<str:external_id>/info/', views.get_work_info, name='get_work_info'),
    path('api/work/<str:external_id>/add_tag/', views.add_tag_to_work, name='add_tag_to_work'),
    path('api/work/<str:external_id>/tags/', views.get_work_tags, name='get_work_tags'),
    path('api/work/<int:work_id>/add_tag/', AddTagView.as_view(), name='add_tag_api'),
    path('my-tags/', views.my_tags, name='my_tags'),

    path('tag/<int:tag_id>/edit/', views.edit_tag, name='edit_tag'),
    path('tag/<int:tag_id>/delete/', views.delete_tag, name='delete_tag'),

    path('delete-account/confirm/', views.confirm_delete_account, name='confirm_delete_account'),
    path('delete-account/', views.delete_account, name='delete_account'),

]


