from django.shortcuts import render

# Create your views here.

def agregarrol(request):
    return render(request, 'rol/agregarrol.html')