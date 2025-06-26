from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
import json
from .models import Candidato, Lista, Cargo
from Aplicaciones.periodo.models import Periodo
from Aplicaciones.padron.models import PadronElectoral
from django.db.models import Q

def buscar_cedula_por_nombre(request):
    nombre = request.GET.get('nombre', '').strip()
    
    if not nombre:
        return JsonResponse({'error': 'Nombre no proporcionado'}, status=400)
    
    try:
        # Imprimir todos los registros para depuración
        print(f"Buscando registros con nombre: {nombre}")
        
        # Buscar en PadronElectoral usando búsqueda parcial insensitive a mayúsculas
        padrones = PadronElectoral.objects.filter(
            Q(nombre__icontains=nombre) | 
            Q(apellidos__icontains=nombre)
        )
        
        # Imprimir número de registros encontrados
        print(f"Registros encontrados: {padrones.count()}")
        
        # Si hay registros, tomar el primero
        padron = padrones.first()
        
        if padron:
            # Imprimir detalles del registro encontrado
            print(f"Registro encontrado - Cédula: {padron.cedula}, Nombre: {padron.nombre} {padron.apellidos}")
            return JsonResponse({
                'cedula': padron.cedula,
                'nombre': f'{padron.nombre} {padron.apellidos}'
            })
        else:
            # Imprimir mensaje si no se encuentra ningún registro
            print(f"No se encontraron registros para: {nombre}")
            return JsonResponse({'error': 'No se encontró ninguna persona'}, status=404)
    
    except Exception as e:
        # Imprimir cualquier error que ocurra
        print(f"Error en buscar_cedula_por_nombre: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def listar_listas(request):
    periodo_actual = Periodo.objects.get(
        fecha_inicio__lte=timezone.now(),
        fecha_fin__gte=timezone.now()
    )
    listas = Lista.objects.filter(periodo=periodo_actual)
    periodos = Periodo.objects.all()
    
    # Obtener todos los candidatos de cada lista con sus cargos
    listas_con_candidatos = []
    for lista in listas:
        # Buscar el presidente
        presidente = Candidato.objects.filter(
            lista=lista,
            cargo__nombre_cargo__icontains='presidente'
        ).first()
        
        # Obtener todos los candidatos de la lista ordenados por cargo
        candidatos = Candidato.objects.filter(
            lista=lista
        ).select_related('cargo').order_by('cargo__nombre_cargo')
        
        # Agregar la lista, presidente y candidatos
        listas_con_candidatos.append({
            'lista': lista,
            'presidente': presidente,
            'candidatos': candidatos
        })
    
    # Convertir mensajes a JSON
    messages_list = [{'message': m.message, 'tags': m.tags} for m in messages.get_messages(request)]
    
    return render(request, 'lista/agregarlista.html', {
        'listas': listas_con_candidatos,
        'periodo_actual': periodo_actual,
        'periodos': periodos,
        'messages_json': json.dumps(messages_list)
    })

def agregar_lista(request):
    periodos = Periodo.objects.all()
    print("\nIntentando agregar nueva lista...")
    print(f"Método de solicitud: {request.method}")
    print(f"POST data: {request.POST}")
    print(f"FILES data: {request.FILES}")
    
    if request.method == 'POST':
        print("Método POST recibido")
        nombre_lista = request.POST.get('nombre_lista', '').strip()
        frase = request.POST.get('frase', '').strip()
        periodo_id = request.POST.get('periodo')
        imagen = request.FILES.get('imagen')
        color = request.POST.get('color', '').strip()
        
        print(f"Datos recibidos:")
        print(f"- Nombre lista: {nombre_lista}")
        print(f"- Frase: {frase}")
        print(f"- Periodo ID: {periodo_id}")
        print(f"- Imagen: {imagen}")
        print(f"- Color: {color}")
        
        # Validar que no haya campos vacíos
        if not nombre_lista:
            print("Error: Nombre de lista vacío")
            messages.error(request, 'El nombre de la lista no puede estar vacío')
            return render(request, 'lista/agregarlista.html', {
                'periodos': periodos,
                'errors': {'nombre_lista': 'El nombre de la lista es obligatorio'}
            })
        
        if not periodo_id:
            print("Error: Periodo no seleccionado")
            messages.error(request, 'Debe seleccionar un periodo')
            return render(request, 'lista/agregarlista.html', {
                'periodos': periodos,
                'errors': {'periodo': 'Seleccione un periodo válido'}
            })
        
        try:
            periodo = Periodo.objects.get(id=periodo_id)
            print(f"Periodo encontrado: {periodo}")
            
            # Verificar si ya existe una lista con el mismo nombre en el periodo
            lista_existente = Lista.objects.filter(
                nombre_lista__iexact=nombre_lista, 
                periodo=periodo
            ).exists()
            
            if lista_existente:
                print(f"Error: Lista {nombre_lista} ya existe en el periodo {periodo}")
                messages.error(request, f'Ya existe una lista con el nombre {nombre_lista} en este periodo')
                return render(request, 'lista/agregarlista.html', {
                    'periodos': periodos,
                    'errors': {'nombre_lista': 'Lista duplicada'}
                })
            
            lista_data = {
                'nombre_lista': nombre_lista,
                'frase': frase,
                'periodo': periodo,
                'imagen': imagen
            }
            
            # Agregar color solo si se proporciona
            if color:
                lista_data['color'] = color
            
            print("Intentando crear lista con datos:", lista_data)
            try:
                lista = Lista.objects.create(**lista_data)
                print(f"Lista creada exitosamente con ID: {lista.id}")
                
                messages.success(request, f'Lista {lista.nombre_lista} creada exitosamente')
                return redirect('listar_listas')
            except Exception as e:
                print(f"Error al crear lista: {str(e)}")
                messages.error(request, f'Error al crear lista: {str(e)}')
                return render(request, 'lista/agregarlista.html', {
                    'periodos': periodos,
                    'errors': {'general': str(e)}
                })
            
        except Periodo.DoesNotExist:
            print(f"Error: No se encontró el periodo con ID {periodo_id}")
            messages.error(request, 'Periodo seleccionado no es válido')
            return render(request, 'lista/agregarlista.html', {
                'periodos': periodos,
                'errors': {'periodo': 'Periodo no válido'}
            })
        except Exception as e:
            print(f"Error al crear la lista: {str(e)}")
            messages.error(request, f'Error al crear la lista: {str(e)}')
            return render(request, 'lista/agregarlista.html', {
                'periodos': periodos,
                'errors': {'general': str(e)}
            })
    
    # GET request
    messages.success(request, 'Lista creada exitosamente')
    return render(request, 'lista/agregarlista.html', {
        'periodos': periodos
    })

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
    messages.success(request, 'Lista actualizada exitosamente')
    return redirect('listar_listas')

def eliminar_lista(request, lista_id):
    if request.method != 'POST':
        return redirect('listar_listas')
        
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
        
        messages.success(request, f'Lista {nombre_lista} y {candidatos_count} candidatos eliminados exitosamente')
        
    except Exception as e:
        messages.error(request, f'No se pudo eliminar la lista. Error: {str(e)}')
        
    return redirect('listar_listas')

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




#APARTADO DE CANDIDATOS
def buscar_nombre_por_cedula(request):
    busqueda = request.GET.get('cedula', '').strip()
    
    try:
        # Si la búsqueda es numérica, buscar por cédula que comience con esos números
        if busqueda.isdigit():
            padron = PadronElectoral.objects.filter(cedula__startswith=busqueda).first()
            if padron:
                return JsonResponse({
                    'nombre': f'{padron.nombre} {padron.apellidos}',
                    'cedula': padron.cedula,
                    'grado': padron.grado.nombre,
                    'paralelo': padron.paralelo.nombre
                })
        
        # Si no es numérica o no se encontró por cédula, buscar por nombre o apellido
        if len(busqueda) >= 3:
            padron = PadronElectoral.objects.filter(
                Q(nombre__icontains=busqueda) | 
                Q(apellidos__icontains=busqueda)
            ).first()
            
            if padron:
                return JsonResponse({
                    'nombre': f'{padron.nombre} {padron.apellidos}',
                    'cedula': padron.cedula,
                    'grado': padron.grado.nombre,
                    'paralelo': padron.paralelo.nombre
                })
        
        return JsonResponse({'nombre': None}, status=404)
        
    except Exception as e:
        print(f'Error en búsqueda: {str(e)}')
        return JsonResponse({'nombre': None}, status=400)

def listar_candidatos(request):
    # Obtener candidatos ordenados por periodo y lista
    candidatos = Candidato.objects.select_related('lista', 'cargo', 'periodo').order_by('periodo__nombre', 'lista__nombre_lista')
    
    # Obtener datos para el formulario
    listas = Lista.objects.all()
    cargos = Cargo.objects.all()
    periodos = Periodo.objects.all()
    
    # Convertir mensajes a JSON para manejar en frontend
    messages_list = [{'message': m.message, 'tags': m.tags} for m in messages.get_messages(request)]
    
    return render(request, 'candidatos/listarcandidatos.html', {
        'candidatos': candidatos,
        'listas': listas,
        'cargos': cargos,
        'periodos': periodos,
        'messages_json': json.dumps(messages_list)
    })

def agregar_candidato(request):
    print('\n' + '='*50)
    print('DEPURACIÓN: Vista de Agregar Candidato')
    print('='*50)
    print(f'Método de solicitud: {request.method}')
    print(f'GET parameters: {request.GET}')
    print(f'POST parameters: {request.POST}')
    print(f'FILES: {request.FILES}')
    
    # Obtener el ID de la lista si se pasa como parámetro
    lista_id = request.GET.get('lista') or request.POST.get('lista')
    lista_preseleccionada = None
    candidatos_existentes = None
    
    if lista_id:
        try:
            lista_preseleccionada = Lista.objects.get(id=lista_id)
            # Obtener los candidatos existentes de la lista
            candidatos_existentes = Candidato.objects.filter(lista=lista_preseleccionada)
        except (Lista.DoesNotExist, ValueError):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Lista no encontrada'}, status=404)
            messages.error(request, 'Lista no encontrada')
            return redirect('listar_candidatos')
    
    if request.method == 'POST':
        # Campos para candidato principal
        cargo_principal_id = request.POST.get('cargo_principal')
        cedula_principal = request.POST.get('cedula_principal', '').strip()
        nombre_principal = request.POST.get('nombre_candidato_principal', '').strip()
        imagen_principal = request.FILES.get('imagen_principal')
        
        # Campos para candidato suplente
        cargo_suplente_id = request.POST.get('cargo_suplente')
        cedula_suplente = request.POST.get('cedula_suplente', '').strip()
        nombre_suplente = request.POST.get('nombre_candidato_suplente', '').strip()
        imagen_suplente = request.FILES.get('imagen_suplente')
        
        # Campos para candidato alterno (opcional)
        cargo_alterno_id = request.POST.get('cargo_alterno')
        cedula_alterno = request.POST.get('cedula_alterno', '').strip()
        nombre_alterno = request.POST.get('nombre_candidato_alterno', '').strip()
        imagen_alterno = request.FILES.get('imagen_alterno')
        
        # Campos comunes
        lista_id = request.POST.get('lista')
        periodo_id = request.POST.get('periodo')
        
        # Validaciones básicas
        if not (nombre_principal and nombre_suplente):
            messages.error(request, 'Los nombres de los candidatos no pueden estar vacíos')
            return redirect('agregar_candidato')
        
        try:
            # Obtener instancias de los modelos
            lista = Lista.objects.get(id=lista_id)
            cargo_principal = Cargo.objects.get(id=cargo_principal_id)
            cargo_suplente = Cargo.objects.get(id=cargo_suplente_id)
            periodo = Periodo.objects.get(id=periodo_id)
            
            # Crear candidatos en una transacción atómica
            from django.db import transaction
            
            try:
                with transaction.atomic():
                    # Buscar en el padrón electoral (sin fallar si no existe)
                    padron_principal = None
                    padron_suplente = None
                    padron_alterno = None
                    
                    # Validar cédulas únicas
                    if cedula_principal and cedula_principal == cedula_suplente:
                        error_msg = 'Las cédulas del candidato principal y suplente no pueden ser iguales'
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({'success': False, 'message': error_msg}, status=400)
                        messages.error(request, error_msg)
                        return redirect('agregar_candidato')
                        
                    if cedula_alterno and (cedula_alterno == cedula_principal or cedula_alterno == cedula_suplente):
                        error_msg = 'La cédula del candidato alterno no puede coincidir con las de los otros candidatos'
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({'success': False, 'message': error_msg}, status=400)
                        messages.error(request, error_msg)
                        return redirect('agregar_candidato')
                    
                    try:
                        if cedula_principal:
                            padron_principal = PadronElectoral.objects.get(cedula=cedula_principal)
                    except PadronElectoral.DoesNotExist:
                        print(f"Advertencia: Cédula {cedula_principal} no encontrada en el padrón")
                        
                    try:
                        if cedula_suplente:
                            padron_suplente = PadronElectoral.objects.get(cedula=cedula_suplente)
                    except PadronElectoral.DoesNotExist:
                        print(f"Advertencia: Cédula {cedula_suplente} no encontrada en el padrón")
                    
                    # Validar cédulas únicas
                    if cedula_principal and cedula_suplente and cedula_principal == cedula_suplente:
                        error_msg = 'Las cédulas de los candidatos deben ser únicas'
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({'success': False, 'message': error_msg}, status=400)
                        messages.error(request, error_msg)
                        return redirect('agregar_candidato')
                    
                    # Crear candidatos en una transacción atómica
                    from django.db import transaction
                    
                    with transaction.atomic():
                        # Crear candidato principal
                        candidato_principal = Candidato.objects.create(
                            nombre_candidato=nombre_principal,
                            lista=lista,
                            cargo=cargo_principal,
                            periodo=periodo,
                            imagen=imagen_principal,
                            padron=padron_principal,
                            tipo_candidato='PRINCIPAL'
                        )
                        
                        # Crear candidato suplente
                        candidato_suplente = Candidato.objects.create(
                            nombre_candidato=nombre_suplente,
                            lista=lista,
                            cargo=cargo_suplente,
                            periodo=periodo,
                            imagen=imagen_suplente,
                            padron=padron_suplente,
                            tipo_candidato='SUPLENTE'
                        )
                        
                        # Crear candidato alterno si se proporciona
                        if cargo_alterno_id and nombre_alterno:
                            try:
                                if cedula_alterno:
                                    padron_alterno = PadronElectoral.objects.get(cedula=cedula_alterno)
                                
                                Candidato.objects.create(
                                    nombre_candidato=nombre_alterno,
                                    lista=lista,
                                    cargo=Cargo.objects.get(id=cargo_alterno_id),
                                    periodo=periodo,
                                    imagen=imagen_alterno,
                                    padron=padron_alterno,
                                    tipo_candidato='ALTERNO'
                                )
                            except PadronElectoral.DoesNotExist:
                                print(f"Advertencia: Cédula {cedula_alterno} no encontrada en el padrón")
                                Candidato.objects.create(
                                    nombre_candidato=nombre_alterno,
                                    lista=lista,
                                    cargo=Cargo.objects.get(id=cargo_alterno_id),
                                    periodo=periodo,
                                    imagen=imagen_alterno,
                                    tipo_candidato='ALTERNO'
                                )
                        
            except Exception as e:
                error_msg = f'Error al crear candidatos: {str(e)}'
                print(error_msg)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': error_msg}, status=500)
                messages.error(request, error_msg)
                return redirect('agregar_candidato')
            
            # Si llegamos aquí, todo salió bien
            success_msg = 'Candidatos guardados exitosamente'
            print(success_msg)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': success_msg,
                    'redirect_url': reverse('listar_candidatos')
                })
                
            messages.success(request, success_msg)
            return redirect('listar_candidatos')
            
        except (Lista.DoesNotExist, Cargo.DoesNotExist, Periodo.DoesNotExist) as e:
            error_msg = f'Error al procesar los datos: {str(e)}'
            print(error_msg)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect('agregar_candidato')
            
        except Exception as e:
            error_msg = f'Error inesperado: {str(e)}'
            print(error_msg)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Ocurrió un error inesperado'}, status=500)
            messages.error(request, 'Ocurrió un error inesperado')
            return redirect('agregar_candidato')
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'data': {
                'listas': [{'id': l.id, 'nombre': l.nombre} for l in Lista.objects.all()],
                'cargos': [{'id': c.id, 'nombre': c.nombre_cargo} for c in Cargo.objects.all()],
                'periodos': [{'id': p.id, 'nombre': p.nombre_periodo} for p in Periodo.objects.all()],
                'lista_preseleccionada': lista_preseleccionada.id if lista_preseleccionada else None
            }
        })
    
    # Cargar datos para el formulario en petición normal
    listas = Lista.objects.all()
    cargos = list(Cargo.objects.all())
    periodos = Periodo.objects.all()
    
    # Inicializar variables para el contexto
    context = {
        'listas': listas,
        'cargos': cargos,
        'periodos': periodos,
        'lista_preseleccionada': lista_preseleccionada,
        'candidatos_existentes': candidatos_existentes or [],
        'candidato_principal': None,
        'candidato_suplente': None,
        'candidato_alterno': None
    }
    
    # Si hay candidatos existentes, cargarlos
    if candidatos_existentes:
        for candidato in candidatos_existentes:
            if candidato.cargo.nombre_cargo.lower() == 'principal':
                context['candidato_principal'] = candidato
            elif candidato.cargo.nombre_cargo.lower() == 'suplente':
                context['candidato_suplente'] = candidato
            elif candidato.cargo.nombre_cargo.lower() == 'alterno':
                context['candidato_alterno'] = candidato
    
    return render(request, 'candidatos/agregarcandidato.html', context)

def editar_candidato(request, candidato_id=None):
    # Obtener datos comunes para GET y POST
    listas = Lista.objects.all()
    cargos = Cargo.objects.all()
    periodos = Periodo.objects.all()
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            lista_id = request.POST.get('lista')
            periodo_id = request.POST.get('periodo')
            
            # Validar datos requeridos
            if not (lista_id and periodo_id):
                messages.error(request, 'Faltan datos requeridos')
                return redirect('listar_candidatos')
                
            # Obtener instancias de modelos
            lista = Lista.objects.get(id=lista_id)
            periodo = Periodo.objects.get(id=periodo_id)
            
            # Función para procesar cada tipo de candidato
            def procesar_candidato(tipo_candidato):
                prefix = tipo_candidato.lower()
                candidato_id = request.POST.get(f'{prefix}_id')
                
                if not candidato_id:  # No hay candidato de este tipo
                    return None
                    
                # Obtener datos del formulario
                nombre = request.POST.get(f'nombre_candidato_{prefix}', '').strip()
                cedula = request.POST.get(f'cedula_{prefix}', '').strip()
                cargo_id = request.POST.get(f'cargo_{prefix}')
                imagen = request.FILES.get(f'imagen_{prefix}')
                
                if not (nombre and cedula and cargo_id):
                    return None
                
                # Buscar en el padrón electoral
                try:
                    padron = PadronElectoral.objects.get(cedula=cedula)
                except PadronElectoral.DoesNotExist:
                    messages.warning(request, f'Cédula {cedula} no encontrada en el padrón electoral')
                    padron = None
                
                # Obtener o crear el cargo
                cargo = Cargo.objects.get(id=cargo_id)
                
                # Actualizar o crear el candidato
                try:
                    if candidato_id != 'new':  # Actualizar existente
                        candidato = Candidato.objects.get(
                            id=candidato_id,
                            lista=lista,
                            tipo_candidato=tipo_candidato
                        )
                        candidato.nombre_candidato = nombre
                        candidato.cargo = cargo
                        if imagen:
                            candidato.imagen = imagen
                        candidato.padron = padron
                        candidato.save()
                    else:  # Crear nuevo
                        candidato = Candidato.objects.create(
                            nombre_candidato=nombre,
                            lista=lista,
                            cargo=cargo,
                            periodo=periodo,
                            imagen=imagen,
                            padron=padron,
                            tipo_candidato=tipo_candidato
                        )
                    return candidato
                    
                except Candidato.DoesNotExist:
                    messages.error(request, f'Error al procesar el {tipo_candidato.lower()}')
                    return None
            
            # Procesar cada tipo de candidato
            with transaction.atomic():
                # Procesar candidato principal
                candidato_principal = procesar_candidato('PRINCIPAL')
                if not candidato_principal:
                    raise Exception('El candidato principal es requerido')
                
                # Procesar candidato suplente
                candidato_suplente = procesar_candidato('SUPLENTE')
                if not candidato_suplente:
                    raise Exception('El candidato suplente es requerido')
                
                # Procesar candidato alterno (opcional)
                candidato_alterno = procesar_candidato('ALTERNO')
            
            messages.success(request, 'Candidatos actualizados exitosamente')
            return redirect('listar_candidatos')
            
        except Exception as e:
            messages.error(request, f'Error al procesar el formulario: {str(e)}')
            return redirect('listar_candidatos')
    
    # GET request - Mostrar formulario de edición
    context = {
        'listas': listas,
        'cargos': cargos,
        'periodos': periodos,
        'candidato_principal': None,
        'candidato_suplente': None,
        'candidato_alterno': None
    }
    
    if candidato_id:
        try:
            # Obtener el candidato principal
            candidato_principal = get_object_or_404(Candidato, id=candidato_id)
            lista = candidato_principal.lista
            
            # Obtener los otros candidatos de la misma lista
            otros_candidatos = Candidato.objects.filter(
                lista=lista,
                periodo=candidato_principal.periodo
            ).exclude(id=candidato_id)
            
            # Asignar a las variables según su tipo
            for candidato in [candidato_principal] + list(otros_candidatos):
                if candidato.tipo_candidato == 'PRINCIPAL':
                    context['candidato_principal'] = candidato
                elif candidato.tipo_candidato == 'SUPLENTE':
                    context['candidato_suplente'] = candidato
                elif candidato.tipo_candidato == 'ALTERNO':
                    context['candidato_alterno'] = candidato
            
        except Exception as e:
            messages.error(request, f'Error al cargar los datos: {str(e)}')
            return redirect('listar_candidatos')
    
    return render(request, 'candidatos/agregarcandidato.html', context)


def eliminar_candidato(request, candidato_id):
    try:
        candidato = get_object_or_404(Candidato, id=candidato_id)
        nombre_candidato = candidato.nombre_candidato
        lista_id = candidato.lista.id if candidato.lista else None
        candidato.delete()
        messages.success(request, f'Candidato {nombre_candidato} eliminado exitosamente')
        
        # Redirigir a la lista de candidatos o a la página anterior
        if lista_id:
            return redirect('listar_candidatos') + f'?lista={lista_id}'
        return redirect('listar_candidatos')
    except Exception as e:
        messages.error(request, f'Error al eliminar candidato: {str(e)}')
        return redirect('listar_candidatos')
    return redirect('listar_candidatos')
