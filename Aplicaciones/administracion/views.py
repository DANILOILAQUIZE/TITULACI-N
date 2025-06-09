from django.shortcuts import render, redirect

# Create your views here.
def index(request):
    return render(request, 'index.html')

def dashboard(request):
    return render(request, 'rol/dashboard.html')

def plantilla(request):
    return render(request, 'administracion/plantilla.html')

def mision_vision(request):
    return render(request, 'administracion/mision_vision.html')

def nosotros(request):
    return render(request, 'administracion/nosotros.html')

def docentes(request):
    return render(request, 'administracion/docentes.html')

def docentes_nuevo(request):
    return render(request, 'administracion/docentes-nuevo.html')

