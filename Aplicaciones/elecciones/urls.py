from django.urls import path
from . import views

urlpatterns = [
    path('buscar_nombre_por_cedula/', views.buscar_nombre_por_cedula, name='buscar_nombre_por_cedula'),
    path('buscar_cedula_por_nombre/', views.buscar_cedula_por_nombre, name='buscar_cedula_por_nombre'),
    path('listas/', views.listar_listas, name='listar_listas'),
    path('lista/nueva/', views.agregar_lista, name='nueva_lista'),
    path('lista/editar/<int:lista_id>/', views.editar_lista, name='editar_lista'),
    path('lista/eliminar/<int:lista_id>/', views.eliminar_lista, name='eliminar_lista'),


    # Rutas de Cargos
    path('cargo/', views.listar_cargos, name='listar_cargos'),
    path('cargo/nuevo/', views.agregar_cargo, name='nuevo_cargo'),
    path('cargo/editar/<int:cargo_id>/', views.agregar_cargo, name='editar_cargo'),
    path('cargo/eliminar/<int:cargo_id>/', views.eliminar_cargo, name='eliminar_cargo'),

    # Rutas de Candidatos
    path('candidatos/', views.listar_candidatos, name='listar_candidatos'),
    path('candidato/nuevo/', views.agregar_candidato, name='agregar_candidato'),
    path('candidato/editar/<int:candidato_id>/', views.editar_candidato, name='editar_candidato'),
    path('candidato/eliminar/<int:candidato_id>/', views.eliminar_candidato, name='eliminar_candidato'),
]