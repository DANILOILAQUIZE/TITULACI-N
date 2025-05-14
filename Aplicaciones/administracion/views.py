from django.shortcuts import render, redirect

# Create your views here.
def index(request):
    return render(request, 'index.html')

def dashboard(request):
    return render(request, 'rol/dashboard.html')

def plantilla(request):
    return render(request, 'administracion/plantilla.html')

