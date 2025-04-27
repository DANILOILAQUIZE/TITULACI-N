from django.shortcuts import render

# Create your views here.
def agregarlista(request):
    return render(request, 'lista/agregarlista.html')