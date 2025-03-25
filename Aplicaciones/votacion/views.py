from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def plantilla(request):
    return render(request, 'plantilla.html')