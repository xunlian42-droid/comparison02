from django.urls import path, include, re_path
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
    # 静的html
    path('tags_html_folder/01_a_tags_processed/static/', lambda r: render(r, 'comparison/tags_html_folder/01_a_tags_processed.html'), name='01_a_tags'),
    path('tags_html_folder/02_ka_tags_processed/static/', lambda r: render(r, 'comparison/tags_html_folder/02_ka_tags_processed.html'), name='02_ka_tags'),
    path('tags_html_folder/03_sa_tags_processed/static/', lambda r: render(r, 'comparison/tags_html_folder/03_sa_tags_processed.html'), name='03_sa_tags'),
    path('tags_html_folder/04_ta_tags_processed/static/', lambda r: render(r, 'comparison/tags_html_folder/04_ta_tags_processed.html'), name='04_ta_tags'),
    path('tags_html_folder/05_na_tags_processed/static/', lambda r: render(r, 'comparison/tags_html_folder/05_na_tags_processed.html'), name='05_na_tags'),
    path('tags_html_folder/06_ha_tags_processed/static/', lambda r: render(r, 'comparison/tags_html_folder/06_ha_tags_processed.html'), name='06_ha_tags'),
    path('tags_html_folder/07_ma_tags_processed/static/', lambda r: render(r, 'comparison/tags_html_folder/07_ma_tags_processed.html'), name='07_ma_tags'),
    path('tags_html_folder/08_ya_tags_processed/static/', lambda r: render(r, 'comparison/tags_html_folder/08_ya_tags_processed.html'), name='08_ya_tags'),
    path('tags_html_folder/09_ra_tags_processed/static/', lambda r: render(r, 'comparison/tags_html_folder/09_ra_tags_processed.html'), name='09_ra_tags'),
    path('tags_html_folder/10_wa_tags_processed/static/', lambda r: render(r, 'comparison/tags_html_folder/10_wa_tags_processed.html'), name='10_wa_tags'),
    path('tags_html_folder/all_tags_combined/static/', lambda r: render(r, 'comparison/tags_html_folder/all_tags_combined.html'), name='all_tags'),
    
    # 動的表示html
    path('tags_html_folder/01_a_tags_processed/', views.popup_tag_file, {'tag_filename': '01_a_tags_processed.html'}, name='popup_01_a_tags'),
    path('tags_html_folder/02_ka_tags_processed/', views.popup_tag_file, {'tag_filename': '02_ka_tags_processed.html'}, name='popup_02_ka_tags'),
    path('tags_html_folder/03_sa_tags_processed/', views.popup_tag_file, {'tag_filename': '03_sa_tags_processed.html'}, name='popup_03_sa_tags'),
    path('tags_html_folder/04_ta_tags_processed/', views.popup_tag_file, {'tag_filename': '04_ta_tags_processed.html'}, name='popup_04_ta_tags'),
    path('tags_html_folder/05_na_tags_processed/', views.popup_tag_file, {'tag_filename': '05_na_tags_processed.html'}, name='popup_05_na_tags'),
    path('tags_html_folder/06_ha_tags_processed/', views.popup_tag_file, {'tag_filename': '06_ha_tags_processed.html'}, name='popup_06_ha_tags'),
    path('tags_html_folder/07_ma_tags_processed/', views.popup_tag_file, {'tag_filename': '07_ma_tags_processed.html'}, name='popup_07_ma_tags'),
    path('tags_html_folder/08_ya_tags_processed/', views.popup_tag_file, {'tag_filename': '08_ya_tags_processed.html'}, name='popup_08_ya_tags'),
    path('tags_html_folder/09_ra_tags_processed/', views.popup_tag_file, {'tag_filename': '09_ra_tags_processed.html'}, name='popup_09_ra_tags'),
    path('tags_html_folder/10_wa_tags_processed/', views.popup_tag_file, {'tag_filename': '10_wa_tags_processed.html'}, name='popup_10_wa_tags'),

    # ユーザ登録
    path('register/', views.register, name='register'),


    # マイページ
    path('mypage/', views.mypage, name='mypage'),

    path('accounts/', include('django.contrib.auth.urls')),



    # external_id を含む API（URLエンコード対応のため re_path を使用）
    re_path(r'^api/work/(?P<external_id>.+)/info/$', views.get_work_info, name='get_work_info'),
    re_path(r'^api/work/(?P<external_id>.+)/add_tag/$', views.add_tag_to_work, name='add_tag_to_work'),
    re_path(r'^api/work/(?P<external_id>.+)/tags/$', views.get_work_tags, name='get_work_tags'),

    # work_id を使う API（整数ID）

    path('api/work/<int:work_id>/add_tag/', AddTagView.as_view(), name='add_tag_api'),
    path('my-tags/', views.my_tags, name='my_tags'),

    path('tag/<int:tag_id>/edit/', views.edit_tag, name='edit_tag'),
    path('tag/<int:tag_id>/delete/', views.delete_tag, name='delete_tag'),

    path('comparison/comparison_<str:page>_with_links.html', views.comparison_page, name='comparison_page'),

    path('favorite/add/<int:work_id>/', views.add_favorite, name='add_favorite'),
    path('favorite/remove/<int:work_id>/', views.remove_favorite_by_work, name='remove_favorite_by_work'),

    path('favorites/', views.my_favorites, name='my_favorites'),

    path('api/my-favorites/', views.api_my_favorites, name='api_my_favorites'),

    # 単一作品ポップアップ
    path('popup/tags/<int:work_id>/', views.popup_single_work, name='popup_tag_for_work'),

    # タグファイル表示（既存の tag_filename を使うルート）
    path('tags_html_folder/<str:tag_filename>/', views.popup_tag_file, name='popup_tag_file'),

    path('work/<int:work_id>/', views.work_detail, name='work_detail'),

    path('delete-account/confirm/', views.confirm_delete_account, name='confirm_delete_account'),
    path('delete-account/', views.delete_account, name='delete_account'),

    
    path("mylist/create/", views.mylist_create, name="mylist_create"),
    path("mylist/<int:pk>/", views.mylist_detail, name="mylist_detail"),
    path("mylist/add/<int:work_id>/", views.add_to_mylist, name="add_to_mylist"),
    path("mylist/<int:pk>/remove/<int:work_id>/", views.remove_from_mylist, name="remove_from_mylist"),
    path("mylist/<int:pk>/delete/", views.delete_mylist, name="delete_mylist")
]


