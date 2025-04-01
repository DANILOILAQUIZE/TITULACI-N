import datetime
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
import pandas as pd
from openpyxl import Workbook
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
import string
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Grado, Paralelo, PadrónElectoral
from django.contrib.auth import get_user_model
def gestion_padron(request):
    # Obtener todos los grados y paralelos ordenados
    grados = Grado.objects.all().order_by('nombre')
    paralelos = Paralelo.objects.all().order_by('grado__nombre', 'nombre')
    
    # Manejar búsqueda y filtros
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', 'activo')
    
    estudiantes = PadrónElectoral.objects.all().order_by('grado__nombre', 'paralelo__nombre', 'apellidos', 'nombre')
    
    if query:
        estudiantes = estudiantes.filter(
            Q(cedula__icontains=query) |
            Q(nombre__icontains=query) |
            Q(apellidos__icontains=query) |
            Q(correo__icontains=query)
        )
    
    if estado in ['activo', 'inactivo']:
        estudiantes = estudiantes.filter(estado=estado)
    
    # Paginación
    paginator = Paginator(estudiantes, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'grados': grados,
        'paralelos': paralelos,
        'estudiantes': page_obj,
        'query': query,
        'estado': estado,
    }
    return render(request, 'padron/agregarPadron.html', context)

# Operaciones CRUD para Grados
def agregar_grado(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre').strip()
        if Grado.objects.filter(nombre=nombre).exists():
            messages.error(request, '¡Este grado ya existe!')
        else:
            Grado.objects.create(nombre=nombre)
            messages.success(request, 'Grado agregado correctamente')
    return redirect('gestion_padron')

def editar_grado(request, id):
    grado = get_object_or_404(Grado, id=id)
    if request.method == 'POST':
        nombre = request.POST.get('nombre').strip()
        if Grado.objects.filter(nombre=nombre).exclude(id=id).exists():
            messages.error(request, '¡Este grado ya existe!')
        else:
            grado.nombre = nombre
            grado.save()
            messages.success(request, 'Grado actualizado correctamente')
    return redirect('gestion_padron')

def eliminar_grado(request, id):
    grado = get_object_or_404(Grado, id=id)
    grado.delete()
    messages.success(request, 'Grado eliminado correctamente')
    return redirect('gestion_padron')

# Operaciones CRUD para Paralelos
def agregar_paralelo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre').strip().upper()
        grado_id = request.POST.get('grado')
        
        grado = get_object_or_404(Grado, id=grado_id)
        if Paralelo.objects.filter(nombre=nombre, grado=grado).exists():
            messages.error(request, '¡Este paralelo ya existe para este grado!')
        else:
            Paralelo.objects.create(nombre=nombre, grado=grado)
            messages.success(request, 'Paralelo agregado correctamente')
    return redirect('gestion_padron')

def editar_paralelo(request, id):
    paralelo = get_object_or_404(Paralelo, id=id)
    if request.method == 'POST':
        nombre = request.POST.get('nombre').strip().upper()
        grado_id = request.POST.get('grado')
        
        grado = get_object_or_404(Grado, id=grado_id)
        if Paralelo.objects.filter(nombre=nombre, grado=grado).exclude(id=id).exists():
            messages.error(request, '¡Este paralelo ya existe para este grado!')
        else:
            paralelo.nombre = nombre
            paralelo.grado = grado
            paralelo.save()
            messages.success(request, 'Paralelo actualizado correctamente')
    return redirect('gestion_padron')

def eliminar_paralelo(request, id):
    paralelo = get_object_or_404(Paralelo, id=id)
    paralelo.delete()
    messages.success(request, 'Paralelo eliminado correctamente')
    return redirect('gestion_padron')

def get_paralelos_by_grado(request):
    grado_id = request.GET.get('grado_id')
    paralelos = Paralelo.objects.filter(grado_id=grado_id).order_by('nombre')
    data = [{'id': p.id, 'nombre': p.nombre} for p in paralelos]
    return JsonResponse(data, safe=False)

# Operaciones CRUD para Estudiantes
def agregar_estudiante(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula').strip()
        nombre = request.POST.get('nombre').strip().title()
        apellidos = request.POST.get('apellidos').strip().title()
        correo = request.POST.get('correo').strip().lower()
        grado_id = request.POST.get('grado')
        paralelo_id = request.POST.get('paralelo')
        
        if PadrónElectoral.objects.filter(cedula=cedula).exists():
            messages.error(request, '¡Esta cédula ya está registrada!')
            return redirect('gestion_padron')
        
        if PadrónElectoral.objects.filter(correo=correo).exists():
            messages.error(request, '¡Este correo ya está registrado!')
            return redirect('gestion_padron')
        
        grado = get_object_or_404(Grado, id=grado_id)
        paralelo = get_object_or_404(Paralelo, id=paralelo_id)
        
        if paralelo.grado != grado:
            messages.error(request, 'El paralelo seleccionado no pertenece al grado especificado')
            return redirect('gestion_padron')
        
        PadrónElectoral.objects.create(
            cedula=cedula,
            nombre=nombre,
            apellidos=apellidos,
            correo=correo,
            grado=grado,
            paralelo=paralelo,
            estado='activo'
        )
        
        messages.success(request, 'Estudiante agregado correctamente')
    return redirect('gestion_padron')

def editar_estudiante(request, id):
    estudiante = get_object_or_404(PadrónElectoral, id=id)
    if request.method == 'POST':
        nombre = request.POST.get('nombre').strip().title()
        apellidos = request.POST.get('apellidos').strip().title()
        correo = request.POST.get('correo').strip().lower()
        grado_id = request.POST.get('grado')
        paralelo_id = request.POST.get('paralelo')
        
        if PadrónElectoral.objects.filter(correo=correo).exclude(id=id).exists():
            messages.error(request, '¡Este correo ya está registrado para otro estudiante!')
            return redirect('gestion_padron')
        
        grado = get_object_or_404(Grado, id=grado_id)
        paralelo = get_object_or_404(Paralelo, id=paralelo_id)
        
        if paralelo.grado != grado:
            messages.error(request, 'El paralelo seleccionado no pertenece al grado especificado')
            return redirect('gestion_padron')
        
        estudiante.nombre = nombre
        estudiante.apellidos = apellidos
        estudiante.correo = correo
        estudiante.grado = grado
        estudiante.paralelo = paralelo
        estudiante.save()
        
        messages.success(request, 'Estudiante actualizado correctamente')
    return redirect('gestion_padron')

def cambiar_estado_estudiante(request, id):
    estudiante = get_object_or_404(PadrónElectoral, id=id)
    if request.method == 'POST':
        estudiante.estado = 'inactivo' if estudiante.estado == 'activo' else 'activo'
        estudiante.save()
        messages.success(request, f'Estudiante {"activado" if estudiante.estado == "activo" else "desactivado"} correctamente')
    return redirect('gestion_padron')

def importar_estudiantes_excel(request):
    if request.method == 'POST' and request.FILES.get('archivo_excel'):
        try:
            if not Grado.objects.exists():
                messages.error(request, 'Primero debe crear al menos un grado')
                return redirect('gestion_padron')
                
            archivo = request.FILES['archivo_excel']
            sobreescribir = request.POST.get('sobreescribir') == 'on'
            
            df = pd.read_excel(archivo)
            
            columnas_requeridas = ['Cédula', 'Nombres', 'Apellidos', 'Correo', 'Grado', 'Paralelo']
            for col in columnas_requeridas:
                if col not in df.columns:
                    messages.error(request, f'Falta la columna requerida: {col}')
                    return redirect('gestion_padron')
            
            contador = 0
            for _, fila in df.iterrows():
                try:
                    cedula = str(fila['Cédula']).strip()
                    nombre = str(fila['Nombres']).strip().title()
                    apellidos = str(fila['Apellidos']).strip().title()
                    correo = str(fila['Correo']).strip().lower()
                    grado_nombre = str(fila['Grado']).strip()
                    paralelo_nombre = str(fila['Paralelo']).strip().upper()
                    
                    if not all([cedula, nombre, apellidos, correo, grado_nombre, paralelo_nombre]):
                        continue
                    
                    grado, _ = Grado.objects.get_or_create(nombre=grado_nombre)
                    paralelo, _ = Paralelo.objects.get_or_create(
                        nombre=paralelo_nombre,
                        grado=grado
                    )
                    
                    estudiante_existente = PadrónElectoral.objects.filter(cedula=cedula).first()
                    
                    if estudiante_existente:
                        if sobreescribir:
                            estudiante_existente.nombre = nombre
                            estudiante_existente.apellidos = apellidos
                            estudiante_existente.correo = correo
                            estudiante_existente.grado = grado
                            estudiante_existente.paralelo = paralelo
                            estudiante_existente.estado = 'activo'
                            estudiante_existente.save()
                            contador += 1
                    else:
                        PadrónElectoral.objects.create(
                            cedula=cedula,
                            nombre=nombre,
                            apellidos=apellidos,
                            correo=correo,
                            grado=grado,
                            paralelo=paralelo,
                            estado='activo'
                        )
                        contador += 1
                
                except Exception as e:
                    continue
            
            messages.success(request, f'Se importaron {contador} estudiantes correctamente')
        
        except Exception as e:
            messages.error(request, f'Error al importar el archivo: {str(e)}')
    
    return redirect('gestion_padron')

def descargar_plantilla(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Plantilla Estudiantes"
    
    ws.append(['Cédula', 'Nombres', 'Apellidos', 'Correo', 'Grado', 'Paralelo'])
    ws.append(['1234567890', 'Juan', 'Pérez', 'juan@ejemplo.com', 'Primero', 'A'])
    ws.append(['0987654321', 'María', 'Gómez', 'maria@ejemplo.com', 'Segundo', 'B'])
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=plantilla_estudiantes.xlsx'
    
    wb.save(response)
    
    return response

#GENRERAR USUARIOS Y CONTRASEÑAS ALEATORIAS

User = get_user_model()  # Obtiene el modelo de usuario personalizado

def generar_credenciales(request):
    if request.method == 'POST':
        estudiantes_seleccionados = request.POST.getlist('estudiantes')
        estudiantes = PadrónElectoral.objects.filter(id__in=estudiantes_seleccionados)
        
        for estudiante in estudiantes:
            try:
                # Generar credenciales
                primer_nombre = estudiante.nombre.split()[0].lower()
                ultimo_digito = estudiante.cedula[-1]
                username = f"{primer_nombre}{ultimo_digito}"
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                
                # Crear usuario en el sistema de autenticación
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': estudiante.correo,
                        'password': make_password(password),
                        'is_active': True,
                        'first_name': estudiante.nombre.split()[0],
                        'last_name': estudiante.apellidos.split()[-1] if estudiante.apellidos else '',
                        # Agrega aquí cualquier otro campo requerido por tu modelo Usuarios
                    }
                )
                
                # Guardar las credenciales en el modelo PadrónElectoral
                estudiante.usuario = user  # Asignar el usuario personalizado
                estudiante.usuario_temp = username  # Opcional: guardar temporalmente
                estudiante.contraseña_temp = password  # Opcional: guardar temporalmente
                estudiante.save()
                
                # Preparar y enviar correo
                asunto = "Tus credenciales de acceso al sistema"
                contexto = {
                    'nombre': estudiante.nombre,
                    'apellidos': estudiante.apellidos,
                    'usuario': username,
                    'contraseña': password,
                    'sistema': "Sistema de Votaciones UTC",
                    'fecha': datetime.now().strftime("%d/%m/%Y"),
                    'enlace_login': request.build_absolute_uri('/accounts/login/')
                }
                
                html_message = render_to_string('correo/email_credenciales.html', contexto)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    asunto,
                    plain_message,
                    'darwin.ilaquize1102@utc.edu.ec',
                    [estudiante.correo],
                    html_message=html_message,
                    fail_silently=False,
                )
                
            except Exception as e:
                messages.error(request, f"Error al procesar {estudiante.nombre}: {str(e)}")
                continue
        
        messages.success(request, f"Credenciales generadas y enviadas a {len(estudiantes)} estudiantes")
        return redirect('generar_credenciales')
    
    # GET: Mostrar formulario
    estudiantes = PadrónElectoral.objects.filter(estado='activo').order_by('apellidos', 'nombre')
    return render(request, 'correo/generar_credenciales.html', {
        'estudiantes': estudiantes,
        'total_estudiantes': estudiantes.count()
    })
    
def agregarEmail(request):
    return render(request, 'correo/email_credenciales.html')