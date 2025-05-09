from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
import json

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
    
    # Convertir mensajes a JSON
    messages_list = [{'message': m.message, 'tags': m.tags} for m in messages.get_messages(request)]
    
    return render(request, 'lista/agregarlista.html', {
        'listas': listas,
        'periodo_actual': periodo_actual,
        'periodos': periodos,
        'messages_json': json.dumps(messages_list)
    })

def agregar_lista(request):
    if request.method == 'POST':
      
        nombre_lista = request.POST.get('nombre_lista', '').strip()
        frase = request.POST.get('frase', '').strip()
        periodo_id = request.POST.get('periodo')
        imagen = request.FILES.get('imagen')
        color = request.POST.get('color', '').strip()
        
     
        if not nombre_lista:
            messages.error(request, 'El nombre de la lista no puede estar vacío')
            messages_list = [{'message': m.message, 'tags': m.tags} for m in messages.get_messages(request)]
            return redirect('listar_listas')
        
        try:
          
            periodo = Periodo.objects.get(id=periodo_id)
            
         
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
            messages_list = [{'message': m.message, 'tags': m.tags} for m in messages.get_messages(request)]
            return redirect('listar_listas')
        
        except Periodo.DoesNotExist:
            messages.error(request, 'Periodo seleccionado no es válido')
        except Exception as e:
            messages.error(request, f'Error al crear la lista: {str(e)}')
    
    messages_list = [{'message': m.message, 'tags': m.tags} for m in messages.get_messages(request)]
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
            messages_list = [{'message': m.message, 'tags': m.tags} for m in messages.get_messages(request)]
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
            messages_list = [{'message': m.message, 'tags': m.tags} for m in messages.get_messages(request)]
            return redirect('listar_listas')
        
        except Periodo.DoesNotExist:
            messages.error(request, 'Periodo seleccionado no es válido')
        except Exception as e:
            messages.error(request, f'Error al actualizar la lista: {str(e)}')
    
    messages_list = [{'message': m.message, 'tags': m.tags} for m in messages.get_messages(request)]
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

#APARTADO DE CARGOS
def listar_cargos(request):
    periodo_actual = Periodo.objects.get(
        fecha_inicio__lte=timezone.now(),
        fecha_fin__gte=timezone.now()
    )
    periodos = Periodo.objects.all()
    cargos = Cargo.objects.filter(periodo=periodo_actual)

    # Convertir mensajes a JSON
    messages_list = [{'message': m.message, 'tags': m.tags} for m in messages.get_messages(request)]

    return render(request, 'cargos/agregarcargo.html', {
        'cargos': cargos,
        'periodo_actual': periodo_actual,
        'periodos': periodos,
        'messages_json': json.dumps(messages_list)
    })

def agregar_cargo(request, cargo_id=None):
    periodo_actual = Periodo.objects.get(
        fecha_inicio__lte=timezone.now(),
        fecha_fin__gte=timezone.now()
    )
    periodos = Periodo.objects.all()
    cargo = None
    
    # Si se proporciona cargo_id, es una edición
    if cargo_id:
        cargo = get_object_or_404(Cargo, id=cargo_id)
    
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre_cargo = request.POST.get('nombre_cargo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        periodo_id = request.POST.get('periodo')
        
        # Validaciones
        if not nombre_cargo:
            messages.error(request, 'El nombre del cargo no puede estar vacío')
            return render(request, 'cargos/agregarcargo.html', {
                'cargo': cargo,
                'periodo_actual': periodo_actual,
                'periodos': periodos
            })
        
        try:
            # Obtener periodo
            periodo = Periodo.objects.get(id=periodo_id)
            
            # Si es edición, actualizar cargo existente
            if cargo:
                cargo.nombre_cargo = nombre_cargo
                cargo.descripcion = descripcion or None
                cargo.periodo = periodo
                cargo.save()
                mensaje = f'El cargo "{cargo.nombre_cargo}" ha sido actualizado exitosamente'
            else:
                # Crear nuevo cargo
                cargo = Cargo.objects.create(
                    nombre_cargo=nombre_cargo,
                    descripcion=descripcion or None,
                    periodo=periodo
                )
                mensaje = f'El cargo "{cargo.nombre_cargo}" ha sido creado exitosamente'
            
            messages.success(request, f'{mensaje} en el periodo {periodo.nombre}')
            return redirect('listar_cargos')
        
        except Periodo.DoesNotExist:
            messages.error(request, 'Periodo seleccionado no es válido')
            return render(request, 'cargos/agregarcargo.html', {
                'cargo': cargo,
                'periodo_actual': periodo_actual,
                'periodos': periodos
            })
        except Exception as e:
            messages.error(request, f'Error al procesar el cargo: {str(e)}')
            return render(request, 'cargos/agregarcargo.html', {
                'cargo': cargo,
                'periodo_actual': periodo_actual,
                'periodos': periodos
            })
    
    # Si no es POST, renderizar la página normalmente
    cargos = Cargo.objects.filter(periodo=periodo_actual)
    messages_list = [{'message': m.message, 'tags': m.tags} for m in messages.get_messages(request)]
    
    return render(request, 'cargos/agregarcargo.html', {
        'cargos': cargos,
        'cargo': cargo,
        'periodo_actual': periodo_actual,
        'periodos': periodos,
        'messages_json': json.dumps(messages_list)
    })

def eliminar_cargo(request, cargo_id):
    if request.method == 'POST':
        try:
            # Obtener el cargo
            cargo = get_object_or_404(Cargo, id=cargo_id)
            
            # Obtener candidatos asociados
            candidatos_asociados = cargo.candidato_set.all()
            candidatos_count = candidatos_asociados.count()
            
            # Eliminar candidatos
            if candidatos_count > 0:
                for candidato in candidatos_asociados:
                    candidato.delete()
            
            # Eliminar el cargo
            nombre_cargo = cargo.nombre_cargo
            cargo.delete()
            
            # Agregar mensaje de éxito
            messages.success(request, f'Cargo {nombre_cargo} eliminado exitosamente')
            
            # Redirigir a la lista de cargos con el mensaje
            return redirect('listar_cargos')
        
        except Exception as e:
            import traceback
            print(f"Error al eliminar cargo: {str(e)}")
            traceback.print_exc()
            
            # Agregar mensaje de error
            messages.error(request, f'No se pudo eliminar el cargo: {str(e)}')
            
            # Redirigir a la lista de cargos con el mensaje de error
            return redirect('listar_cargos')
    else:
        # Mensaje de método no permitido
        messages.error(request, 'Método no permitido')
        return redirect('listar_cargos')