from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView
from .models import Grado, Periodo, Paralelo, PadronElectoral
from django.db import IntegrityError


from Aplicaciones.periodo.models import Periodo
class GradoListView(ListView):
    model = Grado
    template_name = 'grados/agregarGrado.html'
    context_object_name = 'grados'
    paginate_by = 10

    def get_queryset(self):
        return Grado.objects.select_related('periodo').prefetch_related('paralelos').order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # SOLUCIÓN: Usar el último período por fecha de inicio
        context['periodo_actual'] = Periodo.objects.order_by('-fecha_inicio').first()
        return context

def agregar_grado(request):
    # SOLUCIÓN: Obtener el período más reciente por fecha de inicio
    periodo_actual = Periodo.objects.order_by('-fecha_inicio').first()
    
    if not periodo_actual:
        messages.error(request, 'No hay períodos configurados en el sistema')
        return redirect('listar_grados')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        
        if not nombre:
            messages.error(request, 'El nombre del grado es obligatorio')
            return render(request, 'grados/agregarGrado.html', {
                'periodo_actual': periodo_actual,
                'nombre': nombre
            })
        
        try:
            Grado.objects.create(
                nombre=nombre,
                periodo=periodo_actual
            )
            messages.success(request, 'Grado creado exitosamente!')
            return redirect('listar_grados')
        except Exception as e:
            messages.error(request, f'Error al crear grado: {str(e)}')
            return render(request, 'grados/agregar_grado.html', {
                'periodo_actual': periodo_actual,
                'nombre': nombre
            })
    
    return render(request, 'grados/agregar_grado.html', {
        'periodo_actual': periodo_actual
    })


def editar_grado(request, id):
    grado = get_object_or_404(Grado, pk=id)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        
        if not nombre:
            messages.error(request, 'El nombre del grado es obligatorio')
            return render(request, 'grados/editar_grado.html', {
                'grado': grado
            })
        
        try:
            grado.nombre = nombre
            # No modificamos el periodo, se mantiene el que ya tenía
            grado.save()
            messages.success(request, 'Grado actualizado correctamente!')
            return redirect('listar_grados')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
            return render(request, 'grados/editar_grado.html', {
                'grado': grado
            })
    
    return render(request, 'grados/editar_grado.html', {
        'grado': grado
    })

def eliminar_grado(request, id):
    grado = get_object_or_404(Grado, pk=id)
    
    try:
        if grado.padronelectoral_set.exists():
            messages.error(request, 'No se puede eliminar: Existen estudiantes asociados')
        elif grado.paralelos.exists():
            grado.paralelos.all().delete()
            grado.delete()
            messages.success(request, 'Grado y sus paralelos eliminados correctamente')
        else:
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
    paralelos = Paralelo.objects.all()
    
    # Obtener el período actual (el más reciente por fecha de inicio)
    periodo_actual = Periodo.objects.order_by('-fecha_inicio').first()
    
    context = {
        'padron': padron,
        'grados': grados,
        'periodos': periodos,
        'paralelos': paralelos,
        'ESTADOS': ESTADOS,
        'periodo_actual': periodo_actual,  # Añadimos el período actual al contexto
    }
    return render(request, 'padron/agregarPadron.html', context)

def agregar_estudiante(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        cedula = request.POST.get('cedula')
        nombre = request.POST.get('nombre').upper()  # Convertir a mayúsculas como en paralelo
        apellidos = request.POST.get('apellidos').upper()
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        grado_id = request.POST.get('grado')
        paralelo_id = request.POST.get('paralelo')
        periodo_id = request.POST.get('periodo_id')
        estado = request.POST.get('estado')
        
        # Validación básica
        if not all([cedula, nombre, apellidos, correo, grado_id, paralelo_id, estado]):
            messages.error(request, 'Todos los campos obligatorios deben ser completados')
            return redirect('gestion_padron')
        
        try:
            # Verificar si el estudiante ya existe
            if PadronElectoral.objects.filter(cedula=cedula).exists():
                raise IntegrityError('Ya existe un estudiante con esta cédula')
            
            # Si no se proporcionó periodo, usar el actual
            if not periodo_id:
                periodo = Periodo.objects.order_by('-fecha_inicio').first()
                if not periodo:
                    raise ValueError('No hay períodos definidos en el sistema')
                periodo_id = periodo.id
            
            # Crear el estudiante
            PadronElectoral.objects.create(
                cedula=cedula,
                nombre=nombre,
                apellidos=apellidos,
                correo=correo,
                telefono=telefono,
                grado_id=grado_id,
                paralelo_id=paralelo_id,
                periodo_id=periodo_id,
                estado=estado
            )
            
            messages.success(request, 'Estudiante agregado exitosamente!')
            return redirect('gestion_padron')
            
        except IntegrityError as e:
            messages.error(request, f'Error de integridad: {str(e)}')
        except Grado.DoesNotExist:
            messages.error(request, 'El grado seleccionado no existe')
        except Paralelo.DoesNotExist:
            messages.error(request, 'El paralelo seleccionado no existe')
        except Exception as e:
            messages.error(request, f'Error al agregar estudiante: {str(e)}')
        
        return redirect('gestion_padron')
    
    # Si no es POST, mostrar el formulario con los datos necesarios
    return render(request, 'tu_template.html', {
        'grados': Grado.objects.all(),
        'paralelos': Paralelo.objects.all(),
        'periodo_actual': Periodo.objects.order_by('-fecha_inicio').first(),
        'ESTADOS': PadronElectoral.ESTADOS  # Asumiendo que ESTADOS está definido en el modelo
    })

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


# Exportar e importar Padrón Electoral a Excel
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
                    cedula, nombre, apellidos, grado_nombre, paralelo_nombre,Periodo, correo, telefono = row[:8]
                    
                    # Validar campos obligatorios
                    if not all([cedula, nombre, apellidos,  grado_nombre, paralelo_nombre,Periodo,correo]):
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
                            'grado': grado,
                            'paralelo': paralelo,
                            'periodo': Periodo,
                            'correo': correo,
                            'telefono': telefono if telefono else None,
                            
                            'estado': 'activo'
                        }
                    )
            
            messages.success(request, 'Padrón importado exitosamente!')
        except Exception as e:
            messages.error(request, f'Error al importar archivo: {str(e)}')
    
    return redirect('gestion_padron')