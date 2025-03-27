from django.urls import path
from . import views

urlpatterns = [
    
    path('rol/dashboard/', views.dashboard, name='dashboard'),
    
    #CREAMOS LAS VIEWS PARA LOS ROLES
   
    path('rol/agregarrol/', views.agregarrol, name='agregarrol'),
    path('rol/guardarrol/', views.guardarrol, name='guardarrol'),
    path('rol/listarroles/', views.listarroles, name='listarroles'),
    path('editarrol/<int:rol_id>/', views.editarrol, name='editarrol'),
]