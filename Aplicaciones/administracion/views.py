from django.shortcuts import render

# Create your views here.

def dashboard(request):
    return render(request, 'rol/dashboard.html')

def plantilla(request):
    return render(request, 'administracion/plantilla.html')
