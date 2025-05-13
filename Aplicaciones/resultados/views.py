from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from Aplicaciones.votacion.models import ProcesoElectoral, Voto
from Aplicaciones.elecciones.models import Lista
from Aplicaciones.padron.models import PadronElectoral

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
    
    return render(request, 'resultados/resultados.html', context)

def lista_resultados(request):
    procesos = ProcesoElectoral.objects.all().order_by('-created_at')
    return render(request, 'resultados/lista_resultados.html', {
        'procesos': procesos,
        'titulo': 'Resultados de Procesos Electorales'
    })
