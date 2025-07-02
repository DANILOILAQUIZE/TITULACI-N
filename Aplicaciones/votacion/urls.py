from django.urls import path
from . import views
from .views import GenerarCarnetPDF

app_name = 'votacion'

urlpatterns = [
    path('iniciar/', views.iniciar_proceso, name='iniciar_proceso'),
    path('lista/', views.lista_procesos, name='lista_procesos'),
    path('editar/<int:proceso_id>/', views.editar_proceso, name='editar_proceso'),
    path('eliminar/<int:proceso_id>/', views.eliminar_proceso, name='eliminar_proceso'),

    path('obtener-proceso-activo/', views.obtener_proceso_activo, name='obtener_proceso_activo'),

    path('papeleta/<int:proceso_id>/', views.papeleta_votacion, name='papeleta_votacion'),

    path('registrar-voto/<int:proceso_id>/', views.registrar_voto, name='registrar_voto'),
    
    path('resultados/<int:proceso_id>/', views.resultados_votacion, name='resultados_votacion'),
    
    # Ruta para mostrar el carnet de votación
    path('carnet-votacion/', views.mostrar_carnet, name='mostrar_carnet'),
    
    # Ruta para descargar el carnet en PDF
    path('descargar-carnet/<int:carnet_id>/', GenerarCarnetPDF.as_view(), name='descargar_carnet'),
    
    # Ruta para verificar un carnet de votación
    path('verificar-carnet/<str:codigo_verificacion>/', views.verificar_carnet, name='verificar_carnet'),
]