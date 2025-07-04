from django.urls import path
from . import views

app_name = 'noticias'

urlpatterns = [
    # URLs para noticias
    path('listar_noticias/', views.listar_noticias, name='listar_noticias'),
    path('agregar/', views.agregar_noticia, name='agregar_noticia'),
    path('editar/<int:noticia_id>/', views.editar_noticia, name='editar_noticia'),
    path('eliminar/<int:noticia_id>/', views.eliminar_noticia, name='eliminar_noticia'),
    path('ver/<int:noticia_id>/', views.ver_noticia, name='ver_noticia'),
    path('eliminar-imagen/<int:imagen_id>/', views.eliminar_imagen_adicional, name='eliminar_imagen_adicional'),
    
    # URLs para categorías
    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categorias/agregar/', views.agregar_editar_categoria, name='agregar_categoria'),
    path('categorias/editar/<int:categoria_id>/', views.agregar_editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),
]
