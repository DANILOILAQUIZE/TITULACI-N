from django.urls import path
from . import views

urlpatterns = [

    path('', views.dashboard, name='dashboard'),
    path('administracion/plantilla', views.plantilla, name='administracion/plantilla'),
]