from django.urls import path
from . import views
from .views import (
    GradoListView, agregar_grado, editar_grado, eliminar_grado,
    ParaleloListView, agregar_paralelo, editar_paralelo, eliminar_paralelo
    
)

urlpatterns = [
    path('grados/', GradoListView.as_view(), name='listar_grados'),
    path('grados/agregar/', agregar_grado, name='agregar_grado'),
    path('grados/editar/<int:id>/', editar_grado, name='editar_grado'),
    path('grados/eliminar/<int:id>/', eliminar_grado, name='eliminar_grado'),
    
    # URLs para Paralelos
    path('paralelos/', ParaleloListView.as_view(), name='listar_paralelos'),
    path('paralelos/agregar/', agregar_paralelo, name='agregar_paralelo'),
    path('paralelos/editar/<int:id>/', editar_paralelo, name='editar_paralelo'),
    path('paralelos/eliminar/<int:id>/', eliminar_paralelo, name='eliminar_paralelo'),
    
    
    path('padron/', views.gestion_padron, name='gestion_padron'),
    path('padron/agregar/', views.agregar_estudiante, name='agregar_estudiante'),
    path('padron/editar/<int:estudiante_id>/', views.editar_estudiante, name='editar_estudiante'),
    path('padron/eliminar/<int:estudiante_id>/', views.eliminar_estudiante, name='eliminar_estudiante'),
    path('padron/cargar-paralelos/', views.cargar_paralelos, name='cargar_paralelos'),
    path('padron/exportar-excel/', views.exportar_padron_excel, name='exportar_padron_excel'),
    path('padron/importar-excel/', views.importar_padron_excel, name='importar_padron_excel'),
    path('padron/estadisticas/', views.estadisticas_padron, name='estadisticas_padron'),
    path('padron/eliminar-todo/', views.eliminar_todo_el_padron, name='eliminar_todo_el_padron'),
    path('padron/generar-credenciales/', views.generar_credenciales, name='generar_credenciales'),
    path('padron/exportar-credenciales-pdf/', views.exportar_credenciales_pdf, name='exportar_credenciales_pdf'),
    path('padron/enviar-credenciales/', views.enviar_credenciales, name='enviar_credenciales'),
    
    

]
