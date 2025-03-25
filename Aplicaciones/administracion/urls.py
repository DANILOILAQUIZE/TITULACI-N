from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('administracion/plantilla', views.plantilla, name='administracion/plantilla'),
]