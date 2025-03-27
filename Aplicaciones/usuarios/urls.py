from django.urls import path
from . import views
app_name = 'usuarios'
urlpatterns = [
    path('usuarios/agregarrol/', views.agregarrol, name='agregarrol'),
]