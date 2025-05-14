from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name='index'),
    path('', views.dashboard, name='dashboard'),
    path('administracion/plantilla', views.plantilla, name='administracion/plantilla'),
    
  
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)