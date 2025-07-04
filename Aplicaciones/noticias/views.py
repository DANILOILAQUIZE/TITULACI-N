from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Noticia, Categoria
from django.utils import timezone
import os
from django.conf import settings

def listar_noticias(request):
    """
    Vista para listar todas las noticias
    """
    noticias = Noticia.objects.all().order_by('-fecha_publicacion')
    return render(request, 'noticias/noticias/listar_noticias.html', {'noticias': noticias})

def agregar_noticia(request):
    """
    Vista para agregar una nueva noticia
    """
    if request.method == 'POST':
        try:
            # Verificar que el usuario esté autenticado
            if not request.user.is_authenticated:
                messages.error(request, 'Debe iniciar sesión para crear noticias.')
                return redirect('login')  # Ajusta la URL de login según tu configuración
                
            # Obtener datos del formulario
            titulo = request.POST.get('titulo')
            categoria_id = request.POST.get('categoria')
            contenido = request.POST.get('contenido')
            resumen = request.POST.get('resumen', '').strip()  # Obtener el resumen y limpiar espacios en blanco
            estado = request.POST.get('estado', 'borrador')
            
            # Validar campos requeridos
            if not all([titulo, contenido, estado]):
                messages.error(request, 'Los campos título, contenido y estado son obligatorios.')
                return render(request, 'noticias/noticias/agregar_noticia.html', {
                    'categorias': Categoria.objects.filter(activo=True).values('id', 'nombre'),
                    'estados': [('borrador', 'Borrador'), ('publicado', 'Publicado'), ('archivado', 'Archivado')],
                    'form_data': request.POST
                })
            
            # Obtener la categoría
            categoria = None
            if categoria_id:
                categoria = Categoria.objects.get(id=categoria_id)
            
            # Crear la noticia
            noticia = Noticia.objects.create(
                titulo=titulo,
                categoria=categoria,
                contenido=contenido,
                resumen=resumen,
                estado=estado,
                fecha_publicacion=timezone.now()  # Siempre establecer la fecha actual
            )
            
            # Manejar la imagen si se subió
            if 'imagen' in request.FILES:
                noticia.imagen = request.FILES['imagen']
                noticia.save()
            
            messages.success(request, 'Noticia guardada exitosamente.')
            return redirect('noticias:listar_noticias')
            
        except Exception as e:
            messages.error(request, f'Error al guardar la noticia: {str(e)}')
    
    # Si es GET o hay error, mostrar el formulario
    categorias = Categoria.objects.filter(activo=True).values('id', 'nombre')
    estados = [('borrador', 'Borrador'), ('publicado', 'Publicado'), ('archivado', 'Archivado')]
    
    # Crear el contexto con los datos necesarios
    context = {
        'categorias': categorias,
        'estados': estados,
        'form': None  # Asegurarse de que existe un objeto form en el contexto
    }
    
    return render(request, 'noticias/noticias/agregar_noticia.html', context)

def editar_noticia(request, noticia_id):
    """
    Vista para editar una noticia existente
    """
    noticia = get_object_or_404(Noticia, id=noticia_id)
    
    # Verificar que el usuario esté autenticado
    if not request.user.is_authenticated:
        messages.error(request, 'Debe iniciar sesión para editar noticias.')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            # Validar campos requeridos
            titulo = request.POST.get('titulo')
            contenido = request.POST.get('contenido')
            resumen = request.POST.get('resumen', '').strip()
            estado = request.POST.get('estado', 'borrador')
            
            if not all([titulo, contenido, estado]):
                messages.error(request, 'Los campos título, contenido y estado son obligatorios.')
                return render(request, 'noticias/noticias/editar_noticia.html', {
                    'noticia': noticia,
                    'categorias': Categoria.objects.filter(activo=True).values('id', 'nombre'),
                    'estados': [('borrador', 'Borrador'), ('publicado', 'Publicado'), ('archivado', 'Archivado')]
                })
            
            # Actualizar campos básicos
            noticia.titulo = titulo
            noticia.contenido = contenido
            noticia.resumen = resumen if resumen else None
            
            # Actualizar fecha de publicación si el estado cambia a publicado
            estado_anterior = noticia.estado
            noticia.estado = estado
            
            if estado == 'publicado' and (estado_anterior != 'publicado' or not noticia.fecha_publicacion):
                noticia.fecha_publicacion = timezone.now()
            
            # Actualizar categoría
            categoria_id = request.POST.get('categoria')
            if categoria_id:
                noticia.categoria = Categoria.objects.get(id=categoria_id)
            else:
                noticia.categoria = None
            
            # Actualizar imagen si se subió una nueva
            if 'imagen' in request.FILES:
                # Eliminar la imagen anterior si existe
                if noticia.imagen:
                    old_image_path = noticia.imagen.path
                    if os.path.isfile(old_image_path):
                        os.remove(old_image_path)
                noticia.imagen = request.FILES['imagen']
            
            noticia.save()
            
            messages.success(request, 'Noticia actualizada exitosamente.')
            return redirect('noticias:listar_noticias')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar la noticia: {str(e)}')
    
    # Si es GET o hay error, mostrar el formulario
    categorias = Categoria.objects.filter(activo=True)
    return render(request, 'noticias/noticias/editar_noticia.html', {
        'noticia': noticia,
        'categorias': categorias,
        'estados': [('borrador', 'Borrador'), ('publicado', 'Publicado'), ('archivado', 'Archivado')]
    })

def eliminar_noticia(request, noticia_id):
    """
    Vista para eliminar una noticia
    """
    if request.method == 'POST':
        try:
            noticia = get_object_or_404(Noticia, id=noticia_id)
            
            # Eliminar la imagen si existe
            if noticia.imagen:
                image_path = os.path.join(settings.MEDIA_ROOT, str(noticia.imagen))
                if os.path.isfile(image_path):
                    os.remove(image_path)
            
            noticia.delete()
            messages.success(request, 'Noticia eliminada exitosamente.')
            
        except Exception as e:
            messages.error(request, f'Error al eliminar la noticia: {str(e)}')
    
    return redirect('noticias:listar_noticias')

def eliminar_imagen_adicional(request):
    """
    Vista para eliminar una imagen adicional mediante AJAX
    """
    if request.method == 'POST' and request.is_ajax():
        try:
            imagen_id = request.POST.get('imagen_id')
            imagen = get_object_or_404(ImagenNoticia, id=imagen_id)
            
            # Eliminar el archivo de imagen
            if imagen.imagen:
                image_path = os.path.join(settings.MEDIA_ROOT, str(imagen.imagen))
                if os.path.isfile(image_path):
                    os.remove(image_path)
            
            imagen.delete()
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def ver_noticia(request, noticia_id):
    """
    Vista para ver los detalles de una noticia
    """
    noticia = get_object_or_404(Noticia, id=noticia_id)
    
    # Usar la sesión para contar visitas únicas sin depender de la base de datos
    session_key = f'noticia_{noticia_id}_vista'
    contador_key = f'noticia_{noticia_id}_contador'
    
    # Inicializar el contador en la sesión si no existe
    if contador_key not in request.session:
        request.session[contador_key] = 1
    
    # Incrementar el contador solo si es la primera vez que el usuario ve la noticia en esta sesión
    if not request.session.get(session_key, False):
        request.session[contador_key] = request.session.get(contador_key, 1) + 1
        request.session[session_key] = True
        request.session.modified = True
    
    # Obtener noticias relacionadas (misma categoría, excluyendo la actual)
    noticias_relacionadas = Noticia.objects.filter(
        categoria=noticia.categoria,
        estado='publicado'
    ).exclude(id=noticia.id).order_by('-fecha_publicacion')[:3]
    
    return render(request, 'noticias/noticias/ver_noticia.html', {
        'noticia': noticia,
        'noticias_relacionadas': noticias_relacionadas,
        'contador_visitas': request.session.get(contador_key, 1)
    })

# Vistas para la gestión de categorías
def listar_categorias(request):
    """
    Vista para listar todas las categorías
    """
    categorias = Categoria.objects.all().order_by('nombre')
    return render(request, 'noticias/categorias/listar_categorias.html', {
        'categorias': categorias
    })

def agregar_editar_categoria(request, categoria_id=None):
    """
    Vista para agregar o editar una categoría
    """
    if categoria_id:
        categoria = get_object_or_404(Categoria, id=categoria_id)
        titulo = 'Editar Categoría'
    else:
        categoria = None
        titulo = 'Agregar Categoría'
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            color = request.POST.get('color', '#000000')
            activo = 'activo' in request.POST
            
            if not categoria:
                # Crear nueva categoría
                categoria = Categoria.objects.create(
                    nombre=nombre,
                    descripcion=descripcion,
                    color=color,
                    activo=activo
                )
                messages.success(request, 'Categoría creada exitosamente.')
            else:
                # Actualizar categoría existente
                categoria.nombre = nombre
                categoria.descripcion = descripcion
                categoria.color = color
                categoria.activo = activo
                categoria.save()
                messages.success(request, 'Categoría actualizada exitosamente.')
            
            return redirect('noticias:listar_categorias')
            
        except Exception as e:
            messages.error(request, f'Error al guardar la categoría: {str(e)}')
    
    return render(request, 'noticias/categorias/agregar_editar_categoria.html', {
        'categoria': categoria,
        'titulo': titulo
    })

def eliminar_categoria(request, categoria_id):
    """
    Vista para eliminar una categoría
    """
    if request.method == 'POST':
        try:
            categoria = get_object_or_404(Categoria, id=categoria_id)
            
            # Verificar si hay noticias asociadas
            if categoria.noticias.exists():
                messages.error(request, 'No se puede eliminar la categoría porque tiene noticias asociadas.')
            else:
                categoria.delete()
                messages.success(request, 'Categoría eliminada exitosamente.')
                
        except Exception as e:
            messages.error(request, f'Error al eliminar la categoría: {str(e)}')
    
    return redirect('noticias:listar_categorias')
