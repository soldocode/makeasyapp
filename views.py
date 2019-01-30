from django.shortcuts import render


def index(request):
    return render(request,'makeasy/index.html')

#@ensure_csrf_cookie
def item(request):
    return render(request, 'makeasy/item.html')

#@ensure_csrf_cookie
def estimate(request):
    return render(request, 'makeasy/estimate.html')
