from django.urls import path
from . import views

urlpatterns = [
    path('listas/', views.listar_listas, name='listar_listas'),
    path('lista/nueva/', views.agregar_lista, name='nueva_lista'),
    path('lista/editar/<int:lista_id>/', views.editar_lista, name='editar_lista'),
    path('lista/eliminar/<int:lista_id>/', views.eliminar_lista, name='eliminar_lista'),


    # Rutas de Cargos
    path('cargo/', views.listar_cargos, name='listar_cargos'),
    path('cargo/nuevo/', views.agregar_cargo, name='nuevo_cargo'),
    path('cargo/editar/<int:cargo_id>/', views.agregar_cargo, name='editar_cargo'),
    path('cargo/eliminar/<int:cargo_id>/', views.eliminar_cargo, name='eliminar_cargo'),
]