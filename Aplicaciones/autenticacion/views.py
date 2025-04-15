from django.shortcuts import render

# Create your views here.
def agregarLogin(request):
    return render(request, 'login/login.html')