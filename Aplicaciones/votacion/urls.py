from django.urls import path
from . import views

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
]