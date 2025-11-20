from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponseBadRequest, Http404, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from .models import Work, Tag, WorkTag, Favorite
from django.db import IntegrityError, transaction

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View



# Create your views here.
def index(request):
    # トップページ
    return render(request, 'comparison/index.html')


from urllib.parse import unquote

@require_GET
def get_work_info(request, external_id):
    """
    作品の情報を取得するエンドポイント
    """
    # URL から渡された external_id をデコードして整形
    decoded_id = unquote(external_id).strip()

    # 大文字小文字を無視して検索（iexact）
    try:
        work = Work.objects.get(external_id__iexact=decoded_id)
    except Work.DoesNotExist:
        return JsonResponse({
            'error': 'work_not_found',
            'queried_external_id': external_id,
            'decoded_external_id': decoded_id
        }, status=404)

    # お気に入り情報を追加
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, work=work).exists()

    return JsonResponse({
        'id': work.id,
        'title': work.title,
        'external_id': work.external_id,
        'is_favorite': is_favorite
    })

def tag_popup(request):
    # Work と Tag は中間モデル WorkTag を介して関連しているため、work_tags__tag をプリフェッチ
    works = Work.objects.prefetch_related('work_tags__tag').order_by('title')
    return render(request, 'comparison/tag_popup.html', {
        'works': works,
        'all_tags_url': reverse('comparison:all_tags')
    })

def tags_processed(request, gojuon):
    """
    タグ一覧ページを表示する
    """
    # ユーザーのお気に入り情報を取得
    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(
            user=request.user
        ).values_list('work__external_id', flat=True))
    
    return render(request, f'comparison/tags_html_folder/{gojuon}_tags_processed.html', {
        'favorite_ids': favorite_ids
    })

from django.contrib.auth import authenticate, login, logout

# ログイン
def login(request, user):
    user = authenticate(request, username='testuser', password='secret')
    if user is not None:
        login(request, user)  # ログイン処理





from django.db.models import Prefetch

# ログインしていないとアクセスできないビュー
@login_required
def mypage(request):
    # Tag に紐づく Work を事前取得して to_attr= 'user_work_tags' に格納
    work_prefetch = Prefetch(
        'work_tags',               # Tag.work_tags 経由で取得
        queryset=WorkTag.objects.filter(user=request.user).select_related('work'),

        to_attr='user_work_tags'              # テンプレ側から .tag.user_work_tags でアクセスできるようにする
    )

    tags = Tag.objects.filter(
        work_tags__user=request.user      # 必要ならユーザーで絞る（元のロジックに合わせて）
    ).prefetch_related(work_prefetch).distinct()

    sort = request.GET.get("sort", "added")  # デフォルトは追加順

    if sort == "title_asc":
        favorites = Favorite.objects.filter(user=request.user).select_related("work").order_by("work__title")
    elif sort == "title_desc":
        favorites = Favorite.objects.filter(user=request.user).select_related("work").order_by("-work__title")
    else:  # 追加順（idやcreated_atで管理）
        favorites = Favorite.objects.filter(user=request.user).select_related("work").order_by("-id")


    # prepare favorite link_url safely (先のやり取りを踏まえた改善)
    for fav in favorites:
        try:
            fav.link_url = reverse(f"comparison:{fav.work.comparison_page}") + f"#{fav.work.id_for_anchor}"
        except Exception:
            fav.link_url = '#'

    mylists = MyList.objects.filter(user=request.user)

    return render(request, 'comparison/mypage.html', {
        'tags': tags,
        'user': request.user,
        'favorites': favorites,
        "mylists": mylists,
    })




# ログアウト
def logout_view(request):
    logout(request)  # ログアウト処理
    return redirect('comparison')  # トップページへ戻る

# ユーザー登録ビュー
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)  # 入力データをフォームに渡す
        if form.is_valid():
            form.save()  # ユーザーを保存（登録）
            return redirect('login')  # 登録後はログインページへ
    else:
        form = UserCreationForm()  # 空のフォームを表示
    return render(request, 'registration/register.html', {'form': form})


@login_required
def confirm_delete_account(request):
    return render(request, 'comparison/account_confirm_delete.html')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user

        # ユーザーが作成したタグを削除
        Tag.objects.filter(created_by=user).delete()

        # ユーザーを削除
        user.delete()

        # セッション終了
        logout(request)

        return redirect('comparison:index')
    return redirect('comparison:mypage')


def normalize_tag_name(name):
    return name.strip().replace('　', ' ').replace('\u3000', ' ')  # 全角スペース除去

@login_required
@require_POST
def add_tag_to_work(request, external_id):
    tag_name = normalize_tag_name(request.POST.get('tag') or '')
    title = (request.POST.get('title') or '').strip()
    role = (request.POST.get('role') or '未設定').strip()

    if not tag_name:
        return HttpResponseBadRequest('タグ名を指定してください')

    # API 用に未認証時は JSON で返す（念のための二重チェック）
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'ログインが必要です'}, status=403)

    # Work を取得または作成
    work, created_work = Work.objects.get_or_create(
        external_id=external_id,
        defaults={'title': title or external_id}
    )

    tag_obj = None
    tag_created = False
    try:
        with transaction.atomic():
            tag_obj, tag_created = Tag.objects.get_or_create(
                role=role,
                name=tag_name,
                defaults={'created_by': request.user}
            )

            # WorkTagの関連付けを作成
            WorkTag.objects.get_or_create(
                work=work,
                tag=tag_obj,
                user=request.user
            )
    except IntegrityError:
        # 競合などで IntegrityError が出た場合は、既存の Tag を再取得して WorkTag を確保する
        try:
            tag_obj = Tag.objects.get(role=role, name=tag_name)
            tag_created = False
            WorkTag.objects.get_or_create(work=work, tag=tag_obj, user=request.user)
        except Tag.DoesNotExist:
            # 再取得に失敗した場合はエラーとして返す
            return JsonResponse({'status': 'error', 'message': 'タグの作成／取得に失敗しました'}, status=500)

    # 作品に紐づくタグ一覧は WorkTag 経由で取得する
    tags = list(
        WorkTag.objects.filter(work=work)
        .select_related('tag')
        .order_by('tag__role', 'tag__name')
        .values_list('tag__role', 'tag__name')
    )

    # タグ一覧を整形
    tag_strings = [f"{r}:{n}" for r, n in tags]

    return JsonResponse({
        'status': 'ok',
        'tag': f"{tag_obj.role}:{tag_obj.name}",
        'created_work': created_work,
        'created_tag': tag_created,
        'tags': tag_strings
    })

@login_required
@require_GET
def get_work_tags(request, external_id):
    work = Work.objects.filter(external_id=external_id).first()
    if not work:
        return JsonResponse({'status': 'not_found', 'tags': []})

    # タグとそれに関連する全ての作品情報を取得
    tags_with_works = []
    work_tags = (
        WorkTag.objects.filter(work=work)
        .select_related('tag')
        .order_by('tag__role', 'tag__name')
    )
    
    for work_tag in work_tags:
        # 各タグに対して、そのタグを持つ全ての作品を取得
        related_works = (
            Work.objects.filter(work_tags__tag=work_tag.tag)
            .distinct()
            .values('external_id', 'title')
            .order_by('title')
        )
        
        tags_with_works.append({
            'tag': f"{work_tag.tag.role}: {work_tag.tag.name}",
            'related_works': list(related_works)
        })

    return JsonResponse({
        'status': 'ok',
        'work_title': work.title,
        'tags': [t['tag'] for t in tags_with_works],
        'tag_details': tags_with_works
    })



@login_required
def my_tags(request):
    worktag_prefetch = Prefetch(
        'work_tags',
        queryset=WorkTag.objects.filter(user=request.user).select_related('work'),
        to_attr='user_work_tags'
    )

    tags = Tag.objects.filter(work_tags__user=request.user).prefetch_related(worktag_prefetch).distinct()

    return render(request, 'comparison/my_tags.html', {'tags': tags})

@method_decorator(csrf_exempt, name='dispatch')
class AddTagView(View):
    def post(self, request, work_id):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'ログインが必要です'}, status=403)

        work = Work.objects.filter(id=work_id).first()
        if not work:
            return JsonResponse({'error': '作品が見つかりません'}, status=404)

        tag_text = request.POST.get('tag', '').strip()
        if not tag_text or ':' not in tag_text:
            return JsonResponse({'error': 'タグ形式が不正です'}, status=400)

        role, name = tag_text.split(':', 1)
        role = role.strip()
        name = name.strip()

        # Tag を取得または作成し、WorkTag を作成
        tag_obj, tag_created = Tag.objects.get_or_create(
            role=role,
            name=name,
            defaults={'created_by': request.user}
        )
        WorkTag.objects.get_or_create(work=work, tag=tag_obj, user=request.user)

        # 作品のタグ一覧を返す（WorkTag 経由）
        tags = [f"{wt.tag.role}: {wt.tag.name}" for wt in WorkTag.objects.filter(work=work).select_related('tag')]
        return JsonResponse({'tag': f"{tag_obj.role}: {tag_obj.name}", 'tags': tags})

from .forms import TagForm
from django.http import HttpResponseForbidden

@login_required
def edit_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)

    # 自分がこのタグを使っていない場合は403
    if not WorkTag.objects.filter(tag=tag, user=request.user).exists():
        return HttpResponseForbidden("このタグにはアクセスできません。")


    if request.method == 'POST':
        # 作品削除リクエストがある場合
        work_id = request.POST.get('remove_work_id')
        if work_id:
            # WorkTag 経由で関連を削除
            WorkTag.objects.filter(
                tag=tag,
                work_id=work_id,
                user=request.user
            ).delete()
            return redirect('comparison:edit_tag', tag_id=tag.id)

        # 通常のタグ編集（名前変更など）
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            return redirect('comparison:my_tags')
    else:
        form = TagForm(instance=tag)

    # WorkTag 経由で関連する作品を取得
    work_tags = tag.work_tags.select_related('work').filter(user=request.user)
    works = Work.objects.filter(work_tags__in=work_tags).distinct()

    # デバッグ情報
    print(f"Tag {tag.id}: {tag.role}:{tag.name}")
    print(f"Found {works.count()} related works")
    for work in works:
        print(f"- {work.id}: {work.title}")

    return render(request, 'comparison/edit_tag.html', {
        'form': form,
        'tag': tag,
        'works': works,
        'debug_info': {
            'tag_id': tag.id,
            'work_count': works.count(),
        }
    })

@login_required
def delete_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)

    # 自分がこのタグを使っていない場合は削除不可
    if not WorkTag.objects.filter(tag=tag, user=request.user).exists():
        return HttpResponseForbidden("このタグは削除できません。")

    if request.method == 'POST':
        # 自分が追加した WorkTag だけ削除
        WorkTag.objects.filter(tag=tag, user=request.user).delete()

        # 他に誰も使っていなければ Tag 自体も削除
        if not WorkTag.objects.filter(tag=tag).exists():
            tag.delete()

        return redirect('comparison:my_tags')
    

    if request.method == 'POST':
        tag.delete()
        return redirect('comparison:my_tags')
    return render(request, 'comparison/confirm_delete.html', {'tag': tag})



def comparison_page(request, page):
    """
    比較表ページを表示するビュー。
    URLの <str:page> を使ってテンプレート名を構築し、comparison_gojuon_with_links フォルダから読み込む。
    """
    template_name = f'comparison/comparison_gojuon_with_links/comparison_{page}_with_links.html'

    try:
        return render(request, template_name)
    except Exception:
        raise Http404(f"比較表ページ comparison_{page}_with_links.html が見つかりません")



# def _is_ajax_json(request):
#     return request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', '')

# @require_POST
# @login_required
# def add_favorite(request, work_id):
#     work = get_object_or_404(Work, id=work_id)

#     fav, created = Favorite.objects.get_or_create(user=request.user, work=work)

#     # AJAX/Fetch expecting JSON
#     if _is_ajax_json(request):
#         return JsonResponse({
#             'status': 'ok',
#             'action': 'added' if created else 'exists',
#             'work_id': work.id,
#         })

#     # fallback for normal form POST: redirect back or to mypage
#     return redirect(request.META.get('HTTP_REFERER', reverse('comparison:mypage')))

# @require_POST
# @login_required
# def remove_favorite_by_work(request, work_id):
#     work = get_object_or_404(Work, id=work_id)

#     deleted_count, _ = Favorite.objects.filter(user=request.user, work=work).delete()

#     if _is_ajax_json(request):
#         return JsonResponse({
#             'status': 'ok',
#             'action': 'removed' if deleted_count else 'not_found',
#             'work_id': work.id,
#         })

#     return redirect(request.META.get('HTTP_REFERER', reverse('comparison:mypage')))



@require_POST
@login_required
def add_favorite(request, work_id):
    try:
        work = get_object_or_404(Work, id=work_id)
        fav, created = Favorite.objects.get_or_create(user=request.user, work=work)

        return JsonResponse({
            'status': 'ok',
            'action': 'added' if created else 'exists',
            'work_id': work.id,
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
        }, status=400)




@require_POST
@login_required
def remove_favorite_by_work(request, work_id):
    work = get_object_or_404(Work, id=work_id)
    Favorite.objects.filter(user=request.user, work=work).delete()

    # JSONを期待するリクエスト（比較表JS用）
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({'status': 'ok', 'work_id': work.id})

    # 通常のフォームPOST（mypage用）
    return render(request, 'comparison/favorite_removed.html', {
        'work': work
    })



@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('work')
    work_ids = [fav.work.id for fav in favorites if fav.work is not None]
    return JsonResponse({'work_ids': work_ids})

@login_required  # ポップアップでお気に入り登録するならログイン必須
def popup_single_work(request, work_id):

    # work_id が与えられれば単一 Work 用 popup を返す
    if work_id:
        # ポップアップ元の作品IDを GET パラメータから取得
        target_id = request.GET.get('target_id')
        work = get_object_or_404(Work, id=work_id)
        tags = work.tags.all()
        is_favorited = Favorite.objects.filter(user=request.user, work=work).exists()
        return render(request, 'comparison/tags_html_folder/popup_single_work.html', {
            'work': work,
            'tags': tags,
            'target_id': target_id,
            'is_favorited': is_favorited,
            'user': request.user,
        })

@login_required
def popup_tag_file(request, tag_filename):
    # Optional query param: source_external_id - the external_id of the work that opened this tag page
    source_external_id = request.GET.get('source_external_id') or request.GET.get('target_id')

    works = Work.objects.all()
    favorite_ids = set(str(fid) for fid in Favorite.objects.filter(user=request.user).values_list('work_id', flat=True))
    return render(request, f'comparison/tags_html_folder/{tag_filename}', {
        'works': works,
        'favorite_ids': favorite_ids,
        'user': request.user,
        'source_external_id': source_external_id,
    })

@login_required
def work_detail(request, work_id):
    work = get_object_or_404(Work, id=work_id)

    # この作品に紐づくタグ（ManyToManyField 経由）
    tags = work.tags.all()

    # このユーザーがお気に入り登録しているか
    is_favorited = Favorite.objects.filter(user=request.user, work=work).exists()

    return render(request, 'comparison/work_detail.html', {
        'work': work,
        'tags': tags,
        'is_favorited': is_favorited,
    })

from django.db import connection
print(connection.settings_dict)   # 接続先の情報が出る（開発のみ）



@login_required
def api_my_favorites(request):
    # Favorite が work 外部ID（external_id）を参照できる設計を前提にする
    # ここでは Favorite -> work 外部ID を返す
    favs = Favorite.objects.filter(user=request.user).select_related('work')
    external_ids = [f.work.external_id for f in favs if getattr(f.work, 'external_id', None)]
    return JsonResponse({'external_ids': external_ids})




from .models import MyList, MyListItem
from .forms import MyListForm  # 後述するフォーム


# マイリスト詳細：作品一覧を表示
@login_required
def mylist_detail(request, pk):
    mylist = get_object_or_404(MyList, pk=pk, user=request.user)
    return render(request, "comparison/mylist.html", {"mylist": mylist})

# マイリスト作成
@login_required
def mylist_create(request):
    if request.method == "POST":
        form = MyListForm(request.POST)
        if form.is_valid():
            mylist = form.save(commit=False)
            mylist.user = request.user
            mylist.save()
            return redirect("comparison:mylist_detail", pk=mylist.pk)
    else:
        form = MyListForm()
    return render(request, "comparison/mylist_form.html", {"form": form})

# マイリストに作品を追加
@login_required
def add_to_mylist(request, work_id):
    if request.method == "POST":
        mylist_id = request.POST.get("mylist_id")  # フォームから選択されたマイリスト
        mylist = get_object_or_404(MyList, pk= mylist_id, user=request.user)
        work = get_object_or_404(Work, pk=work_id)
        MyListItem.objects.get_or_create(mylist=mylist, work=work)
        return redirect("comparison:mylist_detail", pk=mylist.pk)
    

# マイリストから作品を削除
@login_required
def remove_from_mylist(request, pk, work_id):
    mylist = get_object_or_404(MyList, pk=pk, user=request.user)
    work = get_object_or_404(Work, pk=work_id)
    MyListItem.objects.filter(mylist=mylist, work=work).delete()
    return redirect("comparison:mylist_detail", pk=mylist.pk)

# マイリスト削除
@login_required
def delete_mylist(request, pk):
    mylist = get_object_or_404(MyList, pk=pk, user=request.user)
    if request.method == "POST":
        mylist.delete()
        return redirect("comparison:mypage")
    return render(request, "comparison/confirm_delete_mylist.html", {"mylist": mylist})

