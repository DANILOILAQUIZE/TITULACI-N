from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages

from .models import Lista, Cargo, Candidato, models
from Aplicaciones.periodo.models import Periodo
from Aplicaciones.padron.models import PadronElectoral

def listar_listas(request):
    periodo_actual = Periodo.objects.get(
        fecha_inicio__lte=timezone.now(),
        fecha_fin__gte=timezone.now()
    )
    listas = Lista.objects.filter(periodo=periodo_actual)
    periodos = Periodo.objects.all()
    
    return render(request, 'lista/agregarlista.html', {
        'listas': listas,
        'periodo_actual': periodo_actual,
        'periodos': periodos
    })

def agregar_lista(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre_lista = request.POST.get('nombre_lista', '').strip()
        frase = request.POST.get('frase', '').strip()
        periodo_id = request.POST.get('periodo')
        imagen = request.FILES.get('imagen')
        color = request.POST.get('color', '').strip()
        
        # Validaciones
        if not nombre_lista:
            messages.error(request, 'El nombre de la lista no puede estar vacío')
            return redirect('listar_listas')
        
        try:
            # Obtener periodo
            periodo = Periodo.objects.get(id=periodo_id)
            
            # Crear lista con color personalizado
            lista_data = {
                'nombre_lista': nombre_lista,
                'frase': frase,
                'periodo': periodo,
                'imagen': imagen
            }
            
            # Agregar color solo si se proporciona
            if color:
                lista_data['color'] = color
            
            lista = Lista.objects.create(**lista_data)
            
            messages.success(request, f'Lista {lista.nombre_lista} creada exitosamente')
            return redirect('listar_listas')
        
        except Periodo.DoesNotExist:
            messages.error(request, 'Periodo seleccionado no es válido')
        except Exception as e:
            messages.error(request, f'Error al crear la lista: {str(e)}')
    
    return redirect('listar_listas')

def editar_lista(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id)
    
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre_lista = request.POST.get('nombre_lista', '').strip()
        frase = request.POST.get('frase', '').strip()
        periodo_id = request.POST.get('periodo')
        color = request.POST.get('color', 'azul').strip()
        
        # Validaciones
        if not nombre_lista:
            messages.error(request, 'El nombre de la lista no puede estar vacío')
            return redirect('listar_listas')
        
        try:
            # Actualizar campos
            lista.nombre_lista = nombre_lista
            lista.frase = frase
            
            # Asegurarse de que el color no sea vacío
            if color and color.strip():
                lista.color = color.strip()
            else:
                # Si no se proporciona color, mantener el color existente
                # Si no hay color existente, usar 'azul' como predeterminado
                lista.color = lista.color or 'azul'
            
            # Actualizar periodo si es diferente
            if periodo_id:
                periodo = Periodo.objects.get(id=periodo_id)
                lista.periodo = periodo
            
            # Manejar imagen
            imagen = request.FILES.get('imagen')
            if imagen:
                lista.imagen = imagen
            
            # Guardar cambios
            lista.save()
            
            messages.success(request, f'Lista {lista.nombre_lista} actualizada exitosamente')
            return redirect('listar_listas')
        
        except Periodo.DoesNotExist:
            messages.error(request, 'Periodo seleccionado no es válido')
        except Exception as e:
            messages.error(request, f'Error al actualizar la lista: {str(e)}')
    
    return redirect('listar_listas')

def eliminar_lista(request, lista_id):
    try:
        # Obtener la lista
        lista = get_object_or_404(Lista, id=lista_id)
        
        # Obtener candidatos asociados
        candidatos_asociados = lista.candidato_set.all()
        candidatos_count = candidatos_asociados.count()
        
        # Eliminar candidatos
        if candidatos_count > 0:
            for candidato in candidatos_asociados:
                candidato.delete()
        
        # Eliminar la lista
        nombre_lista = lista.nombre_lista
        lista.delete()
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Lista {nombre_lista} y {candidatos_count} candidatos eliminados exitosamente'
        })
    
    except Exception as e:
        import traceback
        print(f"Error al eliminar lista: {str(e)}")
        traceback.print_exc()
        
        return JsonResponse({
            'status': 'error', 
            'message': f'No se pudo eliminar la lista. Error: {str(e)}'
        })