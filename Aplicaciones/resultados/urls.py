from django.urls import path
from . import views

urlpatterns = [
    path('proceso/<int:proceso_id>/', views.resultados_votacion, name='resultados_votacion'),
    path('lista/', views.lista_resultados, name='lista_resultados'),
]
