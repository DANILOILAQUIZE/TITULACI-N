from django.shortcuts import render, redirect
from .models import Roles, Usuarios
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password

from Aplicaciones.padron.models import PadronElectoral

import random
import string
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
# Create your views here.




def dashboard(request):
    context = {
        'total_usuarios': Usuarios.objects.count(),
        'total_estudiantes': PadronElectoral.objects.count(),
    }
    return render(request, 'rol/dashboard.html', context)

#CREAMOS LAS VIEWS PARA LOS ROLES


def agregarrol(request):
    roles = Roles.objects.all()
    cantidad_roles = roles.count()
    return render(request, 'rol/agregarrol.html', {'roles': roles, 'cantidad_roles': cantidad_roles})

def guardarrol(request):
    nombre_rol=request.POST['nombre_rol']
    descripcion=request.POST['descripcion']
    Roles.objects.create(nombre_rol=nombre_rol, descripcion=descripcion)
    return redirect('agregarrol')

def listarroles(request):
    roles = Roles.objects.all()
    return render(request, 'rol/agregarrol.html', {'roles': roles})

def editar_rol(request, id):
    rol = get_object_or_404(Roles, id=id)
    
    if request.method == "POST":
        nombre_rol = request.POST.get("nombre_rol")
        descripcion = request.POST.get("descripcion", "")

        if nombre_rol:
            rol.nombre_rol = nombre_rol
            rol.descripcion = descripcion
            rol.save()
            messages.success(request, "Rol actualizado correctamente.")
            return redirect('listarroles')
        else:
            messages.error(request, "El nombre del rol es obligatorio.")

    return render(request, 'editar_rol.html', {'rol': rol})

def actualizarrol(request, id):
    rol = Roles.objects.get(id=id)
    rol.nombre_rol = request.POST['nombre_rol']
    rol.descripcion = request.POST['descripcion']
    rol.save()
    return redirect('listarroles')

def eliminarrol(request, id):
    rol = Roles.objects.get(id=id)
    rol.delete()
    return redirect('listarroles')

#CREAMOS LAS VIEWS PARA LOS USUARIOS
# Vista para mostrar la página con la tabla y el modal
def agregarUsuario(request):
    roles = Roles.objects.all()
    usuarios = Usuarios.objects.all()  # Obtener todos los usuarios para la tabla
    return render(request, 'usuarios/agregarUsuario.html', {'roles': roles, 'usuarios': usuarios})

def generar_contraseña_aleatoria(longitud=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))

def guardarUsuario(request):
    if request.method == 'POST':
        cedula = request.POST['cedula']  # Ahora se usa como username
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        email = request.POST['email']
        id_rol = request.POST['id_rol']
        activo = request.POST.get('activo', 'off') == 'on'
        imagen = request.FILES.get('imagen')

        # Verificar si la cédula (username) ya está registrada
        if Usuarios.objects.filter(username=cedula).exists():
            messages.error(request, 'La cédula ya está registrada como nombre de usuario.')
            return redirect('agregarUsuario')

        # Generar contraseña aleatoria
        password_aleatoria = generar_contraseña_aleatoria()

        # Crear usuario
        usuario = Usuarios(
            username=cedula,
            nombre=nombre,
            apellido=apellido,
            email=email,
            password=make_password(password_aleatoria),
            id_rol_id=id_rol,
            activo=activo,
            imagen=imagen
        )
        usuario.save()

        # Enviar la contraseña por correo electrónico
        try:
            send_mail(
                'Credenciales de acceso al Sistema de Votación de la Unidad Educativa Riobamba',
                f'Hola {nombre},{apellido} tu usuario ha sido creado no la pierdas A sido asignado como:{id_rol}.\n\nCédula (usuario): {cedula}\nContraseña: {password_aleatoria}\n\nPor favor, estas credenciales son del consejo electoral',
                'darwin.ilaquize1102@utc.edu.ec',  # Remitente
                [email],
                fail_silently=False,
            )
        except Exception as e:
            messages.warning(request, f'Usuario creado, pero ocurrió un error al enviar el correo: {str(e)}')
            return redirect('agregarUsuario')

        messages.success(request, 'Usuario agregado con éxito y contraseña enviada al correo.')
        return redirect('agregarUsuario')

    roles = Roles.objects.all()
    return render(request, 'usuarios/agregarUsuario.html', {'roles': roles})


def listarUsuarios(request):
    roles = Roles.objects.all()
    usuarios = Usuarios.objects.all()  # Obtiene todos los usuarios

    return render(request, 'usuarios/agregarUsuario.html', {'usuarios': usuarios, 'roles': roles})


def editarUsuario(request, usuario_id):
    usuario = get_object_or_404(Usuarios, id=usuario_id)
    
    if request.method == 'POST':
        try:
            usuario.nombre = request.POST.get('nombre')
            usuario.apellido = request.POST.get('apellido', '')
            usuario.email = request.POST.get('email')
            usuario.username = request.POST.get('username')
            password = request.POST.get('password')
            if password:  # Solo actualizar contraseña si se proporciona
                usuario.set_password(password)
            usuario.id_rol_id = request.POST.get('id_rol')
            usuario.activo = request.POST.get('activo', 'off') == 'on'
            if 'imagen' in request.FILES:
                usuario.imagen = request.FILES['imagen']
            usuario.save()
            messages.success(request, 'Usuario actualizado con éxito.')
        except Exception as e:
            messages.error(request, f'Error al actualizar el usuario: {str(e)}')
        return redirect('agregarUsuario')
    
    usuarios = Usuarios.objects.all()
    roles = Roles.objects.all()
    return render(request, 'usuarios/agregarUsuario.html', {
        'usuarios': usuarios,
        'roles': roles,
        'usuario': usuario
    })


def eliminarUsuario(request, id):
    # Obtener al usuario con el id proporcionado
    usuario = get_object_or_404(Usuarios, id=id)

    # Eliminar el usuario definitivamente
    usuario.delete()
    messages.success(request, "Usuario eliminado con éxito.")

    # Redirigir a la vista donde se listan/agregan usuarios
    return redirect('agregarUsuario')


