from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('administracion/plantilla/', views.plantilla, name='administracion/plantilla'),
    path('mision-vision/', views.mision_vision, name='mision_vision'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('docentes/', views.docentes, name='docentes'),
    path('docentes-nuevo/', views.docentes_nuevo, name='docentes-nuevo'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)