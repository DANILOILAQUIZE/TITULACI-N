from django.urls import path
from . import views

urlpatterns = [
    path('listas/', views.listar_listas, name='listar_listas'),
    path('lista/nueva/', views.agregar_lista, name='nueva_lista'),
    path('lista/editar/<int:lista_id>/', views.editar_lista, name='editar_lista'),
    path('lista/eliminar/<int:lista_id>/', views.eliminar_lista, name='eliminar_lista'),
]