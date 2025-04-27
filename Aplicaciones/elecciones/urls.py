from django.urls import path
from . import views

urlpatterns = [
   
    path('lista/agregarlista/', views.agregarlista, name='agregarlista'),
]