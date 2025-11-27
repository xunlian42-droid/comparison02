from django.shortcuts import render, HttpResponse

# Create your views here.
# product


def test(request):
    # test動作用 path('test/', views.test, name='test'),
    return HttpResponse("product:test")
