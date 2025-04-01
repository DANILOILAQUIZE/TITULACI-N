from django.urls import path
from . import views
from .views import generar_credenciales
urlpatterns = [
    # Vista principal
    path('gestion-padron/', views.gestion_padron, name='gestion_padron'),
    
    # Grados
    path('grados/agregar/', views.agregar_grado, name='agregar_grado'),
    path('grados/editar/<int:id>/', views.editar_grado, name='editar_grado'),
    path('grados/eliminar/<int:id>/', views.eliminar_grado, name='eliminar_grado'),
    
    # Paralelos
    path('paralelos/agregar/', views.agregar_paralelo, name='agregar_paralelo'),
    path('paralelos/editar/<int:id>/', views.editar_paralelo, name='editar_paralelo'),
    path('paralelos/eliminar/<int:id>/', views.eliminar_paralelo, name='eliminar_paralelo'),
    path('paralelos/get-by-grado/', views.get_paralelos_by_grado, name='get_paralelos_by_grado'),
    
    # Estudiantes
    path('estudiantes/agregar/', views.agregar_estudiante, name='agregar_estudiante'),
    path('estudiantes/editar/<int:id>/', views.editar_estudiante, name='editar_estudiante'),
    path('estudiantes/cambiar-estado/<int:id>/', views.cambiar_estado_estudiante, name='cambiar_estado_estudiante'),
    path('estudiantes/importar-excel/', views.importar_estudiantes_excel, name='importar_estudiantes_excel'),
    path('estudiantes/descargar-plantilla/', views.descargar_plantilla, name='descargar_plantilla'),

    #Contraseñas
    
    path('correo/generar-credenciales/', generar_credenciales, name='generar_credenciales'),
    path('correo/agregarEmail/', views.agregarEmail, name='agregarEmail'),
]