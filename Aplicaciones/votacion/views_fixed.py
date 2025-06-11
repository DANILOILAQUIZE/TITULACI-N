from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from .models import ProcesoElectoral, Voto
from Aplicaciones.periodo.models import Periodo
from Aplicaciones.elecciones.models import Lista, Candidato
from Aplicaciones.padron.models import PadronElectoral
import hashlib

def generar_hash_voto(proceso_id, votante_id, timestamp):
    return hashlib.sha256(f"{proceso_id}-{votante_id}-{timestamp}".encode()).hexdigest()

def registrar_voto(request, proceso_id):
    if request.method != 'POST':
        return redirect('papeleta_votacion', proceso_id=proceso_id)
    
    # Verificar si el usuario está autenticado
    if not request.user.is_authenticated:
        messages.error(request, 'Debe iniciar sesión para registrar un voto')
        return redirect('administracion:index')
    
    # Obtener el ID del padrón de la sesión
    padron_id = request.session.get('padron_id')
    if not padron_id:
        messages.error(request, 'No se encontró la información del padrón. Por favor, inicie sesión nuevamente.')
        return redirect('administracion:index')
    
    # Obtener el proceso electoral
    proceso = get_object_or_404(ProcesoElectoral, id=proceso_id)
    
    # Verificar si el proceso está activo
    if not proceso.esta_activo():
        messages.error(request, 'El proceso electoral no está activo')
        return redirect('lista_procesos')
    
    # Obtener la información del padrón
    try:
        padron = PadronElectoral.objects.get(id=padron_id)
        
        # Verificar si ya existe un voto para este proceso y votante
        if Voto.objects.filter(proceso_electoral_id=proceso_id, votante=padron).exists():
            messages.error(request, 'Usted ya ha emitido su voto para este proceso electoral')
            return redirect('administracion:index')
            
        # Verificar si el usuario ya votó (compatibilidad con el campo voto en PadronElectoral)
        if hasattr(padron, 'voto') and padron.voto:
            messages.error(request, 'Usted ya ha emitido su voto para este proceso electoral')
            return redirect('administracion:index')
            
    except PadronElectoral.DoesNotExist:
        messages.error(request, 'No se encontró su registro en el padrón electoral')
        return redirect('administracion:index')
    
    # Obtener el tipo de voto y la lista seleccionada
    tipo_voto = request.POST.get('tipo_voto')
    lista_id = request.POST.get('lista')
    
    # Validar que se haya seleccionado un tipo de voto válido
    if not tipo_voto or (tipo_voto == 'lista' and not lista_id):
        messages.error(request, 'Debe seleccionar una opción de voto válida')
        return redirect('papeleta_votacion', proceso_id=proceso_id)
    
    # Crear el registro del voto
    voto = Voto(proceso_electoral=proceso)
    
    if tipo_voto == 'nulo':
        voto.es_nulo = True
        mensaje_exito = 'Su voto nulo ha sido registrado correctamente.'
    elif tipo_voto == 'blanco':
        voto.es_blanco = True
        mensaje_exito = 'Su voto en blanco ha sido registrado correctamente.'
    else:
        lista = get_object_or_404(Lista, id=lista_id)
        voto.lista = lista
        mensaje_exito = f'Su voto por la lista {lista.nombre_lista} ha sido registrado correctamente.'
    
    # Asignar el votante al voto
    voto.votante = padron
    
    # Generar hash único para el voto
    timestamp = timezone.now().timestamp()
    voto.hash_voto = hashlib.sha256(f"{proceso_id}-{padron.id}-{timestamp}".encode()).hexdigest()
    
    # Guardar el voto
    voto.save()
    
    # Actualizar el estado del padrón para indicar que ya votó
    padron.voto = True
    padron.save()
    
    # Registrar el voto (opcional, para auditoría)
    print(f"\nVoto registrado - Proceso: {proceso.nombre}, Estudiante: {padron.nombre} {padron.apellidos}, Cédula: {padron.cedula}, Tipo: {tipo_voto}")
    
    # Cerrar sesión del usuario
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    
    # Mostrar mensaje de éxito y redirigir a la página de inicio
    messages.success(request, mensaje_exito)
    return redirect('administracion:index')
