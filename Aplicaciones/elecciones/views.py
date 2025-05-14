from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
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
    print('\n' + '='*50)
    print('DEPURACIÓN: Vista de Agregar Candidato')
    print('='*50)
    print(f'Método de solicitud: {request.method}')
    print(f'GET parameters: {request.GET}')
    print(f'POST parameters: {request.POST}')
    print(f'FILES: {request.FILES}')
    # Obtener el ID de la lista si se pasa como parámetro
    lista_id = request.GET.get('lista')
    lista_preseleccionada = None
    candidatos_existentes = None
    
    if lista_id:
        try:
            lista_preseleccionada = Lista.objects.get(id=lista_id)
            # Obtener los candidatos existentes de la lista
            candidatos_existentes = Candidato.objects.filter(lista=lista_preseleccionada)
        except Lista.DoesNotExist:
            pass
    
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
            lista = Lista.objects.get(id=lista_id)
            cargo_principal = Cargo.objects.get(id=cargo_principal_id)
            cargo_suplente = Cargo.objects.get(id=cargo_suplente_id)
            periodo = Periodo.objects.get(id=periodo_id)
            
            # Buscar en el padrón electoral
            try:
                padron_principal = PadronElectoral.objects.get(cedula=cedula_principal)
                padron_suplente = PadronElectoral.objects.get(cedula=cedula_suplente)
                padron_alterno = None
                
                # Validar candidato alterno si se proporciona
                if cargo_alterno_id and cedula_alterno and nombre_alterno:
                    padron_alterno = PadronElectoral.objects.get(cedula=cedula_alterno)
            except PadronElectoral.DoesNotExist as e:
                messages.error(request, f'Cédula no encontrada en el padrón electoral: {str(e)}')
                return redirect('agregar_candidato')
            
            # Crear candidatos
            try:
                candidato_principal = Candidato.objects.create(
                    nombre_candidato=nombre_principal,
                    lista=lista,
                    cargo=cargo_principal,
                    periodo=periodo,
                    imagen=imagen_principal,
                    padron=padron_principal
                )
                print(f'Candidato principal creado: {candidato_principal.id}')
                
                candidato_suplente = Candidato.objects.create(
                    nombre_candidato=nombre_suplente,
                    lista=lista,
                    cargo=cargo_suplente,
                    periodo=periodo,
                    imagen=imagen_suplente,
                    padron=padron_suplente
                )
                print(f'Candidato suplente creado: {candidato_suplente.id}')
            except Exception as e:
                print(f'ERROR al crear candidatos: {str(e)}')
                messages.error(request, f'Error al crear candidatos: {str(e)}')
                return render(request, 'candidatos/agregarcandidato.html', {
                    'listas': Lista.objects.all(),
                    'cargos': Cargo.objects.all(),
                    'periodos': Periodo.objects.all(),
                    'errors': {'general': str(e)}
                })
            
            # Candidato alterno (opcional)
            if cargo_alterno_id and nombre_alterno and padron_alterno:
                cargo_alterno = Cargo.objects.get(id=cargo_alterno_id)
                candidato_alterno = Candidato.objects.create(
                    nombre_candidato=nombre_alterno,
                    lista=lista,
                    cargo=cargo_alterno,
                    periodo=periodo,
                    imagen=imagen_alterno,
                    padron=padron_alterno
                )
            
            messages.success(request, 'Candidatos agregados exitosamente')
            return redirect('listar_candidatos')
        
        except (Lista.DoesNotExist, Cargo.DoesNotExist, Periodo.DoesNotExist) as e:
            messages.error(request, f'Error al crear candidatos: {str(e)}')
            return redirect('agregar_candidato')
    
    # GET request
    listas = Lista.objects.all()
    cargos = Cargo.objects.all()
    periodos = Periodo.objects.all()
    
    return render(request, 'candidatos/agregarcandidato.html', {
        'listas': listas,
        'cargos': cargos,
        'periodos': periodos,
        'lista_preseleccionada': lista_preseleccionada,
        'candidatos_existentes': candidatos_existentes
    })

def editar_candidato(request, candidato_id=None):
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
            lista = Lista.objects.get(id=lista_id)
            cargo_principal = Cargo.objects.get(id=cargo_principal_id)
            cargo_suplente = Cargo.objects.get(id=cargo_suplente_id)
            periodo = Periodo.objects.get(id=periodo_id)
            
            # Buscar en el padrón electoral
            try:
                padron_principal = PadronElectoral.objects.get(cedula=cedula_principal)
                padron_suplente = PadronElectoral.objects.get(cedula=cedula_suplente)
                padron_alterno = None
                
                # Validar candidato alterno si se proporciona
                if cargo_alterno_id and cedula_alterno and nombre_alterno:
                    padron_alterno = PadronElectoral.objects.get(cedula=cedula_alterno)
            except PadronElectoral.DoesNotExist as e:
                messages.error(request, f'Cédula no encontrada en el padrón electoral: {str(e)}')
                return redirect('agregar_candidato')
            
            # Si se proporciona un candidato_id, es una edición
            if candidato_id:
                try:
                    # Obtener candidato existente
                    candidato_actual = Candidato.objects.get(id=candidato_id)
                    # Obtener otros candidatos relacionados
                    otros_candidatos = Candidato.objects.filter(
                        lista=candidato_actual.lista,
                        periodo=candidato_actual.periodo
                    ).exclude(id=candidato_id)
                    
                    # Actualizar candidato principal
                    candidato_actual.nombre_candidato = nombre_principal
                    candidato_actual.lista = lista
                    candidato_actual.cargo = cargo_principal
                    candidato_actual.periodo = periodo
                    candidato_actual.padron = padron_principal
                    if imagen_principal:
                        candidato_actual.imagen = imagen_principal
                    candidato_actual.save()
                    
                    # Actualizar o crear suplente
                    if otros_candidatos.exists():
                        candidato_suplente = otros_candidatos[0]
                        candidato_suplente.nombre_candidato = nombre_suplente
                        candidato_suplente.cargo = cargo_suplente
                        candidato_suplente.padron = padron_suplente
                        if imagen_suplente:
                            candidato_suplente.imagen = imagen_suplente
                        candidato_suplente.save()
                    else:
                        candidato_suplente = Candidato.objects.create(
                            nombre_candidato=nombre_suplente,
                            lista=lista,
                            cargo=cargo_suplente,
                            periodo=periodo,
                            imagen=imagen_suplente,
                            padron=padron_suplente
                        )
                    
                    # Actualizar o crear alterno
                    if cargo_alterno_id and nombre_alterno and padron_alterno:
                        cargo_alterno = Cargo.objects.get(id=cargo_alterno_id)
                        if len(otros_candidatos) > 1:
                            candidato_alterno = otros_candidatos[1]
                            candidato_alterno.nombre_candidato = nombre_alterno
                            candidato_alterno.cargo = cargo_alterno
                            candidato_alterno.padron = padron_alterno
                            if imagen_alterno:
                                candidato_alterno.imagen = imagen_alterno
                            candidato_alterno.save()
                        else:
                            candidato_alterno = Candidato.objects.create(
                                nombre_candidato=nombre_alterno,
                                lista=lista,
                                cargo=cargo_alterno,
                                periodo=periodo,
                                imagen=imagen_alterno,
                                padron=padron_alterno
                            )
                    
                except Candidato.DoesNotExist:
                    messages.error(request, 'Candidato no encontrado')
                    return redirect('listar_candidatos')
            else:
                # Crear nuevos candidatos
                candidato_principal = Candidato.objects.create(
                    nombre_candidato=nombre_principal,
                    lista=lista,
                    cargo=cargo_principal,
                    periodo=periodo,
                    imagen=imagen_principal,
                    padron=padron_principal
                )
                
                candidato_suplente = Candidato.objects.create(
                    nombre_candidato=nombre_suplente,
                    lista=lista,
                    cargo=cargo_suplente,
                    periodo=periodo,
                    imagen=imagen_suplente,
                    padron=padron_suplente
                )
                
                # Candidato alterno (opcional)
                if cargo_alterno_id and nombre_alterno and padron_alterno:
                    cargo_alterno = Cargo.objects.get(id=cargo_alterno_id)
                    candidato_alterno = Candidato.objects.create(
                        nombre_candidato=nombre_alterno,
                        lista=lista,
                        cargo=cargo_alterno,
                        periodo=periodo,
                        imagen=imagen_alterno,
                        padron=padron_alterno
                    )
            
            messages.success(request, 'Candidatos actualizados exitosamente')
            return redirect('listar_candidatos')
        
        except (Lista.DoesNotExist, Cargo.DoesNotExist, Periodo.DoesNotExist) as e:
            messages.error(request, f'Error al actualizar candidatos: {str(e)}')
            return redirect('agregar_candidato')
    
    # GET request
    listas = Lista.objects.all()
    cargos = Cargo.objects.all()
    periodos = Periodo.objects.all()
    
    # Si se proporciona candidato_id, cargar sus datos
    candidato_principal = None
    candidato_suplente = None
    candidato_alterno = None
    
    if candidato_id:
        # Obtener el candidato principal por ID
        try:
            candidato_principal = get_object_or_404(Candidato, id=candidato_id)
            # Obtener otros candidatos de la misma lista y periodo
            otros_candidatos = Candidato.objects.filter(
                lista=candidato_principal.lista,
                periodo=candidato_principal.periodo
            ).exclude(id=candidato_id).order_by('id')
            
            # Asignar suplente y alterno si existen
            candidato_suplente = otros_candidatos[0] if otros_candidatos else None
            candidato_alterno = otros_candidatos[1] if len(otros_candidatos) > 1 else None
        except Candidato.DoesNotExist:
            messages.error(request, 'Candidato no encontrado')
            return redirect('listar_candidatos')
    
    return render(request, 'candidatos/agregarcandidato.html', {
        'candidato_principal': candidato_principal,
        'candidato_suplente': candidato_suplente,
        'candidato_alterno': candidato_alterno,
        'listas': listas,
        'cargos': cargos,
        'periodos': periodos
    })

def eliminar_candidato(request, candidato_id):
    try:
        candidato = get_object_or_404(Candidato, id=candidato_id)
        nombre_candidato = candidato.nombre_candidato
        candidato.delete()
        messages.success(request, f'Candidato {nombre_candidato} eliminado exitosamente')
    except Exception as e:
        messages.error(request, f'Error al eliminar candidato: {str(e)}')
    
    return redirect('listar_candidatos')
