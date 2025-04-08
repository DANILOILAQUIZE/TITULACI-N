from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Periodo
from datetime import datetime

# Vista para mostrar la página de periodos con el formulario y la tabla
def agregarPeriodo(request):
    periodos = Periodo.objects.all().order_by('-fecha_inicio')
    return render(request, 'periodo/agregarPeriodo.html', {'periodos': periodos})


# Vista para guardar un nuevo periodo
def guardarPeriodo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')

        if fecha_inicio >= fecha_fin:
            messages.error(request, 'La fecha de fin debe ser posterior a la fecha de inicio.')
            return redirect('agregarPeriodo')

        periodo = Periodo(
            nombre=nombre,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        periodo.save()
        messages.success(request, 'Periodo académico agregado correctamente.')
    return redirect('agregarPeriodo')


# Vista para editar un periodo existente
def editar_periodo(request, id):
    periodo = get_object_or_404(Periodo, id=id)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')

        if fecha_inicio >= fecha_fin:
            messages.error(request, 'La fecha de fin debe ser posterior a la fecha de inicio.')
            return redirect('agregarPeriodo')

        periodo.nombre = nombre
        periodo.fecha_inicio = fecha_inicio
        periodo.fecha_fin = fecha_fin
        periodo.save()

        messages.success(request, 'Periodo académico actualizado correctamente.')
        return redirect('agregarPeriodo')


# Vista para eliminar un periodo
def eliminar_periodo(request, id):
    periodo = get_object_or_404(Periodo, id=id)
    periodo.delete()
    messages.success(request, f'Periodo académico "{periodo.nombre}" eliminado correctamente.')
    return redirect('agregarPeriodo')
