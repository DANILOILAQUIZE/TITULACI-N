from django.urls import path
from . import views

urlpatterns = [
    path('periodo/agregarPeriodo/', views.agregarPeriodo, name='agregarPeriodo'),
    path('guardarPeriodo/', views.guardarPeriodo, name='guardarPeriodo'),
    path('editar-periodo/<int:id>/', views.editar_periodo, name='editar_periodo'),
    path('eliminar-periodo/<int:id>/', views.eliminar_periodo, name='eliminar_periodo'),
]
