from django.shortcuts import render

# Create your views here.

# プロジェクト全体のホームページを表示


def index(request):
    return render(request, 'home/index.html')
