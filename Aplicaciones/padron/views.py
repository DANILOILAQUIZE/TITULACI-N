from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView
from .models import Grado, Periodo, Paralelo, PadronElectoral
from django.db import IntegrityError

#GRADO
class GradoListView(ListView):
    model = Grado
    template_name = 'grados/agregarGrado.html'
    context_object_name = 'grados'
    paginate_by = 10

    def get_queryset(self):
        return Grado.objects.select_related('periodo').prefetch_related('paralelos').order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['periodos'] = Periodo.objects.all()
        return context

def agregar_grado(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        periodo_id = request.POST.get('periodo') or None
        
        if not nombre:
            messages.error(request, 'El nombre del grado es obligatorio')
            return redirect('listar_grados')
        
        try:
            Grado.objects.create(
                nombre=nombre,
                periodo_id=periodo_id
            )
            messages.success(request, 'Grado creado exitosamente!')
        except Exception as e:
            messages.error(request, f'Error al crear grado: {str(e)}')
        
        return redirect('listar_grados')
    
    return render(request, 'grados/agregarGrado.html', {
        'periodos': Periodo.objects.all()
    })
    

def editar_grado(request, id):
    grado = get_object_or_404(Grado, pk=id)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        periodo_id = request.POST.get('periodo') or None
        
        if not nombre:
            messages.error(request, 'El nombre del grado es obligatorio')
            return redirect('listar_grados')
        
        try:
            grado.nombre = nombre
            grado.periodo_id = periodo_id
            grado.save()
            messages.success(request, 'Grado actualizado correctamente!')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
        
        return redirect('listar_grados')
    
    return render(request, 'grado/modals/form_grado.html', {
        'grado': grado,
        'periodos': Periodo.objects.all()
    })

def eliminar_grado(request, id):
    grado = get_object_or_404(Grado, pk=id)
    
    if grado.padronelectoral_set.exists():
        messages.error(request, '¡No se puede eliminar! Existen estudiantes asociados')
    else:
        try:
            grado.delete()
            messages.success(request, 'Grado eliminado correctamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar: {str(e)}')
    
    return redirect('listar_grados')




#PARALELOS
class ParaleloListView(ListView):
    model = Paralelo
    template_name = 'paralelos/agregarParalelo.html'
    context_object_name = 'paralelos'
    paginate_by = 15

    def get_queryset(self):
        return Paralelo.objects.select_related('grado', 'grado__periodo').order_by('grado__nombre', 'nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grados'] = Grado.objects.all()
        return context

def agregar_paralelo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre').upper()
        grado_id = request.POST.get('grado')
        
        if not nombre or not grado_id:
            messages.error(request, 'Todos los campos son obligatorios')
            return redirect('listar_paralelos')
        
        try:
            Paralelo.objects.create(
                nombre=nombre,
                grado_id=grado_id
            )
            messages.success(request, 'Paralelo creado exitosamente!')
        except IntegrityError:
            messages.error(request, 'Este paralelo ya existe para el grado seleccionado')
        except Exception as e:
            messages.error(request, f'Error al crear paralelo: {str(e)}')
        
        return redirect('listar_paralelos')
    
    return render(request, 'paralelos/agregarParalelo.html', {
        'grados': Grado.objects.all()
    })

def editar_paralelo(request, id):
    paralelo = get_object_or_404(Paralelo, pk=id)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre').upper()
        grado_id = request.POST.get('grado')
        
        if not nombre or not grado_id:
            messages.error(request, 'Todos los campos son obligatorios')
            return redirect('listar_paralelos')
        
        try:
            paralelo.nombre = nombre
            paralelo.grado_id = grado_id
            paralelo.save()
            messages.success(request, 'Paralelo actualizado correctamente!')
        except IntegrityError:
            messages.error(request, 'Este paralelo ya existe para el grado seleccionado')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
        
        return redirect('listar_paralelos')
    
    return render(request, 'paralelo/modals/form_paralelo.html', {
        'paralelo': paralelo,
        'grados': Grado.objects.all()
    })

def eliminar_paralelo(request, id):
    paralelo = get_object_or_404(Paralelo, pk=id)
    
    if paralelo.padronelectoral_set.exists():
        messages.error(request, '¡No se puede eliminar! Existen estudiantes asociados')
    else:
        try:
            paralelo.delete()
            messages.success(request, 'Paralelo eliminado correctamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar: {str(e)}')
    
    return redirect('listar_paralelos')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from .models import  Grado, Paralelo, Periodo, PadronElectoral
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
import io

ESTADOS = [
    ('activo', 'Activo'),
    ('inactivo', 'Inactivo'),
]

def gestion_padron(request):
    padron = PadronElectoral.objects.select_related('grado', 'paralelo', 'periodo').all().order_by('apellidos', 'nombre')
    grados = Grado.objects.all().prefetch_related('paralelos')
    periodos = Periodo.objects.all()
    
    context = {
        'padron': padron,
        'grados': grados,
        'periodos': periodos,
        'ESTADOS': ESTADOS,
    }
    return render(request, 'padron/agregarPadron.html', context)

def agregar_estudiante(request):
    if request.method == 'POST':
        try:
            cedula = request.POST.get('cedula')
            nombre = request.POST.get('nombre')
            apellidos = request.POST.get('apellidos')
            correo = request.POST.get('correo')
            telefono = request.POST.get('telefono')
            grado_id = request.POST.get('grado')
            paralelo_id = request.POST.get('paralelo')
            periodo_id = request.POST.get('periodo')
            estado = request.POST.get('estado')
            
            grado = Grado.objects.get(id=grado_id)
            paralelo = Paralelo.objects.get(id=paralelo_id)
            
            estudiante = PadronElectoral(
                cedula=cedula,
                nombre=nombre,
                apellidos=apellidos,
                correo=correo,
                telefono=telefono,
                grado=grado,
                paralelo=paralelo,
                estado=estado
            )
            
            if periodo_id:
                periodo = Periodo.objects.get(id=periodo_id)
                estudiante.periodo = periodo
                
            estudiante.save()
            messages.success(request, 'Estudiante agregado exitosamente!')
        except Exception as e:
            messages.error(request, f'Error al agregar estudiante: {str(e)}')
    
    return redirect('gestion_padron')

def editar_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(PadronElectoral, id=estudiante_id)
    
    if request.method == 'POST':
        try:
            estudiante.cedula = request.POST.get('cedula')
            estudiante.nombre = request.POST.get('nombre')
            estudiante.apellidos = request.POST.get('apellidos')
            estudiante.correo = request.POST.get('correo')
            estudiante.telefono = request.POST.get('telefono')
            estudiante.estado = request.POST.get('estado')
            
            grado_id = request.POST.get('grado')
            paralelo_id = request.POST.get('paralelo')
            periodo_id = request.POST.get('periodo')
            
            estudiante.grado = Grado.objects.get(id=grado_id)
            estudiante.paralelo = Paralelo.objects.get(id=paralelo_id)
            
            if periodo_id:
                estudiante.periodo = Periodo.objects.get(id=periodo_id)
            else:
                estudiante.periodo = None
                
            estudiante.save()
            messages.success(request, 'Estudiante actualizado exitosamente!')
        except Exception as e:
            messages.error(request, f'Error al actualizar estudiante: {str(e)}')
    
    return redirect('gestion_padron')

def eliminar_estudiante(request, estudiante_id):
    estudiante = get_object_or_404(PadronElectoral, id=estudiante_id)
    
    try:
        estudiante.delete()
        messages.success(request, 'Estudiante eliminado exitosamente!')
    except Exception as e:
        messages.error(request, f'Error al eliminar estudiante: {str(e)}')
    
    return redirect('gestion_padron')

def cargar_paralelos(request):
    grado_id = request.GET.get('grado_id')
    paralelos = Paralelo.objects.filter(grado_id=grado_id).order_by('nombre')
    
    data = {
        'paralelos': [{'id': p.id, 'nombre': p.nombre} for p in paralelos]
    }
    return JsonResponse(data)

def exportar_padron_excel(request):
    # Crear el libro de trabajo y la hoja
    wb = Workbook()
    ws = wb.active
    ws.title = "Padrón Electoral"
    
    # Encabezados
    headers = [
        'Cédula', 'Apellidos', 'Nombres', 'Grado', 'Paralelo', 
        'Período', 'Correo Electrónico', 'Teléfono', 'Estado'
    ]
    
    for col_num, header in enumerate(headers, 1):
        col_letter = get_column_letter(col_num)
        ws[f'{col_letter}1'] = header
        ws.column_dimensions[col_letter].width = 20
    
    # Datos
    estudiantes = PadronElectoral.objects.select_related('grado', 'paralelo', 'periodo').all()
    
    for row_num, estudiante in enumerate(estudiantes, 2):
        ws[f'A{row_num}'] = estudiante.cedula
        ws[f'B{row_num}'] = estudiante.apellidos
        ws[f'C{row_num}'] = estudiante.nombre
        ws[f'D{row_num}'] = estudiante.grado.nombre
        ws[f'E{row_num}'] = estudiante.paralelo.nombre
        ws[f'F{row_num}'] = estudiante.periodo.nombre if estudiante.periodo else ''
        ws[f'G{row_num}'] = estudiante.correo
        ws[f'H{row_num}'] = estudiante.telefono if estudiante.telefono else ''
        ws[f'I{row_num}'] = estudiante.get_estado_display()
    
    # Preparar la respuesta
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=padron_electoral.xlsx'
    
    # Guardar el libro en la respuesta
    with io.BytesIO() as buffer:
        wb.save(buffer)
        response.write(buffer.getvalue())
    
    return response

def importar_padron_excel(request):
    if request.method == 'POST' and request.FILES.get('archivo_excel'):
        archivo = request.FILES['archivo_excel']
        
        try:
            wb = load_workbook(archivo)
            ws = wb.active
            
            with transaction.atomic():
                for row in ws.iter_rows(min_row=2, values_only=True):
                    # Asumimos el formato: Cédula | Nombres | Apellidos | Correo | Grado | Paralelo | Teléfono
                    cedula, nombre, apellidos, correo, grado_nombre, paralelo_nombre, telefono = row[:7]
                    
                    # Validar campos obligatorios
                    if not all([cedula, nombre, apellidos, correo, grado_nombre, paralelo_nombre]):
                        continue
                    
                    # Obtener o crear grado y paralelo
                    grado, _ = Grado.objects.get_or_create(nombre=grado_nombre.strip())
                    paralelo, _ = Paralelo.objects.get_or_create(
                        nombre=paralelo_nombre.strip(),
                        grado=grado
                    )
                    
                    # Crear o actualizar estudiante
                    estudiante, created = PadronElectoral.objects.update_or_create(
                        cedula=cedula,
                        defaults={
                            'nombre': nombre,
                            'apellidos': apellidos,
                            'correo': correo,
                            'telefono': telefono if telefono else None,
                            'grado': grado,
                            'paralelo': paralelo,
                            'estado': 'activo'
                        }
                    )
            
            messages.success(request, 'Padrón importado exitosamente!')
        except Exception as e:
            messages.error(request, f'Error al importar archivo: {str(e)}')
    
    return redirect('gestion_padron')