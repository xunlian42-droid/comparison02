from .models import BmiRecord
from django.shortcuts import render
from .forms import BmiRecordForm
from .forms import BmiForm  # BmiForm をインポート
from .forms import ProfileForm
from django.shortcuts import render, HttpResponse
from django.contrib import messages
from django.shortcuts import redirect

# Create your views here.
def hello_view(request):
    simei = None  # HTMLに渡すデータ辞書
    form = None

    if request.method == 'POST':  # フォームがPOST送信されたとき
        # フォームを生成、全送信データをセット
        form = ProfileForm(request.POST)
        # 値のチェック
        if form.is_valid():
            # 適正データ
            simei = form.cleaned_data['simei']
        
    # GET=アドレス指定でアクセス
    else:
        # 空のフォームオブジェクト
        form = ProfileForm()

    return render(request, 'calculator/hello.html', {'form': form, 'simei': simei})


def test(request):
    return HttpResponse("test page OK.")


def bmi_view(request):
    # BMI計算ページのビュー関数
    context = None  # HTMLに渡すデータ辞書

    if request.method == 'POST':  # フォームがPOST送信されたとき
        simei = request.POST['simei']  # お名前を取得
        height = float(request.POST['height'])  # 身長を取得して小数に変換（cm）
        weight = float(request.POST['weight'])  # 体重を取得して小数に変換（kg）
        height_m = height / 100  # cm → m に変換
        bmi = round(weight / (height_m ** 2), 2)  # BMI計算（小数第2位まで）
        context = {'simei': simei,
                   'height': height,
                   'weight': weight, 'bmi': bmi
                   }

    # GET,POSTともにbmi.htmlを表示
    return render(request, template_name='calculator/bmi.html', context=context)


def bmi_form(request):
    # BMI計算フォームクラスで処理するビュー関数
    result = None  # 初期化：計算結果を格納する変数（テンプレートに渡す用）

    # フォームが送信されたかどうかを判定（POSTメソッドかどうか）
    if request.method == 'POST':
        # POSTデータを使ってフォームをインスタンス化（バリデーション対象）
        form = BmiForm(request.POST)

        # フォームの入力がすべて有効かどうかをチェック
        if form.is_valid():
            # バリデーション済みのデータを取得（辞書形式）
            simei = form.cleaned_data['simei']     # お名前
            height = form.cleaned_data['height']   # 身長（cm）
            weight = form.cleaned_data['weight']   # 体重（kg）

            # 身長をメートルに変換（cm → m）
            height_m = height / 100

            # BMIを計算（体重 ÷ 身長²）
            bmi = round(weight / (height_m ** 2), 2)

            # 結果メッセージを作成
            result = f"{simei} さんのBMIは {bmi} です。"

    else:
        # GETリクエストの場合は空のフォームを表示
        form = BmiForm()

    # form.html テンプレートを表示し、フォームと結果を渡す
    return render(request, 'calculator/BmiForm.html', {'form': form, 'result': result})


def bmi_record_form(request):
    # BMIモデルフォームクラスを利用したデータベース登録処理
    if request.method == 'POST':
        form = BmiRecordForm(request.POST)
        if form.is_valid():
            record = form.save()  # データベースに保存
            bmi_value = record.bmi()  # BMIを計算
            return render(request, 'calculator/BmiRecordForm.html', {
                'form': form,
                'bmi': bmi_value,
                'record': record,
                'submitted': True
            })
    else:
        form = BmiRecordForm()
    return render(request, 'calculator/BmiRecordForm.html', {
        'form': form,
        'submitted': False
    })


def bmi_record_list(request):
    # BmiRecordsテーブルの一覧
    records = BmiRecord.objects.all().order_by('-id')  # 新しい順に並べる
    return render(request, 'calculator/bmi_list.html', {'records': records})


def bmi_record_list_edit_delete(request):
    # 編集・削除リンク付き一覧画面
    records = BmiRecord.objects.all().order_by('-id')  # 新しい順に並べる
    return render(request, 'calculator/bmi_list_edit_delete.html', {'records': records})


from django.shortcuts import get_object_or_404
def bmi_record_edit(request, id):
    # idで検索
    record = get_object_or_404(BmiRecord, pk=id)

    # ボタンを押されたときの処理
    if request.method == 'POST':
        # 検索結果と送信データの突合せ
        # POSTデータと既存のレコードを使ってフォームを生成（instance指定で更新モードになる）。
        form = BmiRecordForm(request.POST, instance=record)

        # フォームのバリデーション（入力チェック）を実行。
        if form.is_valid():
            # 入力が正しければ、フォームの内容でレコードを保存（更新）。
            form.save()

            # 更新成功メッセージを表示（テンプレート側で messages を使って表示可能。 ※messagesは自動でhtmlに渡される）。
            messages.success(request, '更新しました')

            # 一覧画面にリダイレクト（URL名 'calculator:bmi_record_list_edit_delete' が定義されている必要あり）。
            return redirect('calculator:bmi_record_list_edit_delete')
    else:
        # 編集フォーム入力内容をセット：オブジェクト生成
        form = BmiRecordForm(instance=record)

    # フォームをテンプレートに渡して表示。テンプレート 'calculator/bmi_form.html' を使用。
    return render(request, 'calculator/bmi_edit_form.html', {'form': form})


def bmi_record_delete(request, id):
    # 指定されたIDに対応するBmiRecordオブジェクトを取得。存在しない場合は404エラー画面を表示。
    record = get_object_or_404(BmiRecord, pk=id)
    # リクエストがPOST（削除ボタンが押された）だった場合、削除処理を実行する。
    if request.method == 'POST':
        # 対象のレコードをデータベースから削除する。
        record.delete()

        # 削除成功メッセージを表示（テンプレート側で messages を使って表示可能）。
        messages.success(request, '削除しました')

        # 一覧画面にリダイレクト（URL名 'calculator:bmi_record_list_edit_delete' が定義されている必要あり）。
        return redirect('calculator:bmi_record_list_edit_delete')

    # GETリクエストの場合（削除確認画面の表示）、対象レコードをテンプレートに渡して表示。
    return render(request, 'calculator/bmi_confirm_delete.html', {'record': record})
