from django.shortcuts import render, HttpResponse, redirect
from .forms import UserForm
from user.models import User
from django.contrib import messages

# Create your views here.
# user


def test(request):
    # test動作用 path('test/', views.test, name='test'),
    return HttpResponse("user:test")


def register_user(request):
    # ユーザ登録 path('register/', views.register_user, name='register'),
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            # urls.pyのname=に記したURLパターン名にリダイレクト(F5キー押下による二重登録防止対策)
            return redirect('user:thanks')  

    else:
        form = UserForm()
    return render(request, 'user/register.html', {'form': form})



def thanks(request):
    # ユーザ登録完了 path('thanks/', views.thanks, name='thanks'),
    return render(request, 'user/thanks.html')

def list_view(request):
    messages.success(request, "保存が完了しました！")
    messages.error(request, "エラーが発生しました。")

    # Userデータの全権検索
    records = User.objects.all()
    print(records)
    return render(request, 'user/list.html', {'records':records})
