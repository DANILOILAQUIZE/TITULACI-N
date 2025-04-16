from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [

   
    path('configuracion/agregar_logo/', views.agregar_logo, name='agregar_logo'),
    path('configuracion-logo/', views.configurar_logo, name='configurar_logo'),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)