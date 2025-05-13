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
    texto = f"{proceso_id}-{votante_id}-{timestamp}"
    return hashlib.sha256(texto.encode()).hexdigest()

def iniciar_proceso(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        periodo_id = request.POST.get('periodo')
        fecha = request.POST.get('fecha')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        descripcion = request.POST.get('descripcion')

        try:
            periodo = get_object_or_404(Periodo, id=periodo_id)
            
            proceso = ProcesoElectoral(
                nombre=nombre,
                periodo=periodo,
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                descripcion=descripcion
            )
            proceso.save()
            
            messages.success(request, 'Proceso electoral creado exitosamente')
            return redirect('lista_procesos')
        except Exception as e:
            messages.error(request, f'Error al crear el proceso: {str(e)}')
            return redirect('iniciar_proceso')

    # Obtener los períodos activos
    periodos = Periodo.objects.filter(estado='activo')
    return render(request, 'votacion/proceso/iniciar.html', {'periodos': periodos})

def lista_procesos(request):
    procesos = ProcesoElectoral.objects.all().order_by('-fecha', '-hora_inicio')
    
    # Actualizar estados automáticamente
    for proceso in procesos:
        proceso.actualizar_estado()
    
    periodos = Periodo.objects.filter(estado='activo')
    
    return render(request, 'votacion/proceso/lista.html', {
        'procesos': procesos,
        'periodos': periodos,
        'titulo': 'Lista de Procesos Electorales'
    })

def editar_proceso(request, proceso_id):
    try:
        proceso = get_object_or_404(ProcesoElectoral, id=proceso_id)
        periodos = Periodo.objects.filter(estado='activo')
        
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            periodo_id = request.POST.get('periodo')
            fecha = request.POST.get('fecha')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')
            descripcion = request.POST.get('descripcion')

            periodo = get_object_or_404(Periodo, id=periodo_id)
            
            proceso.nombre = nombre
            proceso.periodo = periodo
            proceso.fecha = fecha
            proceso.hora_inicio = hora_inicio
            proceso.hora_fin = hora_fin
            proceso.descripcion = descripcion
            proceso.save()
            
            messages.success(request, 'Proceso electoral actualizado exitosamente')
            return redirect('lista_procesos')
        else:
            return render(request, 'votacion/proceso/editar.html', {
                'proceso': proceso,
                'periodos': periodos,
                'titulo': 'Editar Proceso Electoral'
            })
    except Exception as e:
        messages.error(request, f'Error al editar el proceso: {str(e)}')
        return redirect('lista_procesos')

def eliminar_proceso(request, proceso_id):
    try:
        proceso = get_object_or_404(ProcesoElectoral, id=proceso_id)
        
        if request.method == 'POST':
            proceso.delete()
            messages.success(request, 'Proceso electoral eliminado exitosamente')
            return redirect('lista_procesos')
        else:
            return render(request, 'votacion/proceso/eliminar.html', {
                'proceso': proceso,
                'titulo': 'Eliminar Proceso Electoral'
            })
    except Exception as e:
        messages.error(request, f'Error al eliminar el proceso: {str(e)}')
        return redirect('lista_procesos')

def obtener_proceso_activo(request):
    # Buscar el primer proceso activo
    try:
        procesos = ProcesoElectoral.objects.all()
        proceso_activo = None
        
        # Buscar el primer proceso que esté activo
        for proceso in procesos:
            if proceso.esta_activo():
                proceso_activo = proceso
                break
        
        if proceso_activo:
            return redirect('papeleta_votacion', proceso_id=proceso_activo.id)
        else:
            messages.warning(request, 'No hay procesos electorales activos en este momento')
            return redirect('lista_procesos')
    except Exception as e:
        messages.error(request, f'Error al buscar proceso activo: {str(e)}')
        return redirect('lista_procesos')

def papeleta_votacion(request, proceso_id):
    proceso = get_object_or_404(ProcesoElectoral, id=proceso_id)
    
    if not proceso.esta_activo():
        messages.error(request, 'El proceso electoral no está activo')
        return redirect('lista_procesos')
    
    print(f"\nProceso electoral: {proceso.nombre}")
    print(f"Periodo del proceso: {proceso.periodo}")
    
    # Obtener todas las listas del periodo
    listas = Lista.objects.filter(periodo=proceso.periodo)
    print(f"Número de listas encontradas: {listas.count()}")
    for lista in listas:
        print(f"- Lista: {lista.nombre_lista}")
    
    listas_con_candidatos = []
    
    for lista in listas:
        candidatos = Candidato.objects.filter(
            lista=lista
        ).select_related('cargo').order_by('cargo__nombre_cargo')
        
        print(f"\nCandidatos para lista {lista.nombre_lista}:")
        for candidato in candidatos:
            print(f"- {candidato.cargo.nombre_cargo}: {candidato.nombre_candidato}")
        
        listas_con_candidatos.append({
            'lista': lista,
            'candidatos': candidatos
        })

    context = {
        'proceso': proceso,
        'listas_con_candidatos': listas_con_candidatos
    }
    
    return render(request, 'votacion/papeleta.html', context)

def registrar_voto(request, proceso_id):
    if request.method != 'POST':
        return redirect('papeleta_votacion', proceso_id=proceso_id)

    proceso = get_object_or_404(ProcesoElectoral, id=proceso_id)
    
    if not proceso.esta_activo():
        messages.error(request, 'El proceso electoral no está activo')
        return redirect('lista_procesos')

    # Aquí deberías obtener el votante de alguna manera
    # Por ahora, podemos usar un votante de prueba o dejarlo pendiente
    # hasta implementar la autenticación
    tipo_voto = request.POST.get('tipo_voto')
    lista_id = request.POST.get('lista')

    # Por ahora, no asignamos votante al voto
    voto = Voto(proceso_electoral=proceso)
    
    if tipo_voto == 'nulo':
        voto.es_nulo = True
    elif tipo_voto == 'blanco':
        voto.es_blanco = True
    else:
        lista = get_object_or_404(Lista, id=lista_id)
        voto.lista = lista

    # Generar hash único para el voto
    timestamp = timezone.now().timestamp()
    # Por ahora usamos solo el timestamp para el hash
    voto.hash_voto = generar_hash_voto(proceso.id, 0, timestamp)
    voto.save()

    messages.success(request, 'Voto registrado exitosamente')
    return redirect('resultados_votacion', proceso_id=proceso_id)

def resultados_votacion(request, proceso_id):
    proceso = get_object_or_404(ProcesoElectoral, id=proceso_id)
    
    # Obtener votos por lista
    votos_por_lista = Voto.objects.filter(
        proceso_electoral=proceso,
        lista__isnull=False
    ).values('lista').annotate(total=Count('id'))
    
    # Obtener total de votos
    total_votos = Voto.objects.filter(proceso_electoral=proceso).count()
    votos_blancos = Voto.objects.filter(proceso_electoral=proceso, es_blanco=True).count()
    votos_nulos = Voto.objects.filter(proceso_electoral=proceso, es_nulo=True).count()
    
    # Calcular porcentajes
    resultados_por_lista = []
    for voto in votos_por_lista:
        lista = Lista.objects.get(id=voto['lista'])
        porcentaje = (voto['total'] / total_votos * 100) if total_votos > 0 else 0
        resultados_por_lista.append({
            'lista': lista,
            'votos': voto['total'],
            'porcentaje': porcentaje
        })
    
    # Calcular porcentajes de blancos y nulos
    porcentaje_blancos = (votos_blancos / total_votos * 100) if total_votos > 0 else 0
    porcentaje_nulos = (votos_nulos / total_votos * 100) if total_votos > 0 else 0
    
    # Obtener estadísticas de participación
    total_votantes = PadronElectoral.objects.filter(periodo=proceso.periodo).count()
    faltan_votar = total_votantes - total_votos
    porcentaje_participacion = (total_votos / total_votantes * 100) if total_votantes > 0 else 0
    
    context = {
        'proceso': proceso,
        'resultados_por_lista': resultados_por_lista,
        'votos_blancos': votos_blancos,
        'votos_nulos': votos_nulos,
        'porcentaje_blancos': porcentaje_blancos,
        'porcentaje_nulos': porcentaje_nulos,
        'total_votos': total_votos,
        'total_votantes': total_votantes,
        'faltan_votar': faltan_votar,
        'porcentaje_participacion': porcentaje_participacion
    }
    
    return render(request, 'votacion/resultados.html', context)
