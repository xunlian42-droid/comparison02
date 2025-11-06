from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from .models import Work, Tag, WorkTag
from django.db import IntegrityError, transaction

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View



# Create your views here.
def index(request):
    # トップページ
    return render(request, 'comparison/index.html')

@require_GET
def get_work_info(request, external_id):
    """
    作品の情報を取得するエンドポイント
    """
    work = get_object_or_404(Work, external_id=external_id)
    return JsonResponse({
        'id': work.id,
        'title': work.title,
        'external_id': work.external_id,
    })

def tag_popup(request):
    # Work と Tag は中間モデル WorkTag を介して関連しているため、work_tags__tag をプリフェッチ
    works = Work.objects.prefetch_related('work_tags__tag').order_by('title')
    return render(request, 'comparison/tag_popup.html', {
        'works': works,
        'all_tags_url': reverse('comparison:all_tags')
    })

from django.contrib.auth import authenticate, login, logout

# ログイン
def login(request, user):
    user = authenticate(request, username='testuser', password='secret')
    if user is not None:
        login(request, user)  # ログイン処理

# ログインしていないとアクセスできないビュー
@login_required
def mypage(request):
    # WorkTagを介してユーザーが付けたタグを取得
    tags = Tag.objects.filter(
        work_tags__user=request.user
    ).select_related(
        'created_by'
    ).prefetch_related(
        'work_tags__work'
    ).distinct()
    
    # ログインユーザー情報は request.user に格納されている
    return render(request, 'comparison/mypage.html', {
        'tags': tags,
        'user': request.user
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
    tags = Tag.objects.filter(created_by=request.user).prefetch_related('work_tags__work')
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

@login_required
def edit_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id, created_by=request.user)

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

    return render(request, 'comparison/edit_tag.html', {
        'form': form,
        'tag': tag,
        # 作品一覧は中間モデル WorkTag 経由で取得する（DB に古い M2M テーブルが存在しない可能性があるため）
        'works': [wt.work for wt in tag.work_tags.all()]
    })

@login_required
def delete_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id, created_by=request.user)
    if request.method == 'POST':
        tag.delete()
        return redirect('comparison:my_tags')
    return render(request, 'comparison/confirm_delete.html', {'tag': tag})

