from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    
    path('rol/dashboard/', views.dashboard, name='dashboard'),
    
    #CREAMOS LAS VIEWS PARA LOS ROLES
   
    path('rol/agregarrol/', views.agregarrol, name='agregarrol'),
    path('rol/guardarrol/', views.guardarrol, name='guardarrol'),
    path('rol/listarroles/', views.listarroles, name='listarroles'),
    path('editar_rol/<int:id>/', views.editar_rol, name='editar_rol'),
    path('actualizarrol/<int:id>/', views.actualizarrol, name='actualizarrol'),
    path('eliminarrol/<int:id>/', views.eliminarrol, name='eliminarrol'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)