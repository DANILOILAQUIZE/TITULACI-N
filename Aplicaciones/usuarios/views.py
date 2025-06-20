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
        print('Método POST recibido')
        print('POST data:', request.POST)
        print('FILES:', request.FILES)
        
        try:
            # Validar que todos los campos requeridos estén presentes
            required_fields = ['cedula', 'nombre', 'email', 'id_rol']
            for field in required_fields:
                if field not in request.POST or not request.POST[field].strip():
                    messages.error(request, f'El campo {field} es obligatorio')
                    return redirect('agregarUsuario')
            
            # Obtener datos del formulario
            cedula = request.POST['cedula'].strip()
            nombre = request.POST['nombre'].strip()
            apellido = request.POST.get('apellido', '').strip()
            email = request.POST['email'].strip()
            id_rol = request.POST['id_rol']
            activo = request.POST.get('activo', 'off') == 'on'
            imagen = request.FILES.get('imagen')
            
            print('Datos extraídos correctamente:')
            print(f'Cédula: {cedula}')
            print(f'Nombre: {nombre}')
            print(f'Apellido: {apellido}')
            print(f'Email: {email}')
            print(f'Rol ID: {id_rol}')
            print(f'Activo: {activo}')
            print(f'Imagen: {imagen}')

            # Verificar si la cédula (username) ya está registrada
            if Usuarios.objects.filter(username=cedula).exists():
                messages.error(request, 'La cédula ya está registrada como nombre de usuario.')
                return redirect('agregarUsuario')
                
            # Verificar si el correo ya está registrado
            if Usuarios.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ya está registrado.')
                return redirect('agregarUsuario')

            # Generar contraseña aleatoria
            password_aleatoria = generar_contraseña_aleatoria()
            print(f'Contraseña generada: {password_aleatoria}')

            try:
                # Crear usuario usando create_user para manejar correctamente la contraseña
                usuario = Usuarios.objects.create_user(
                    username=cedula,
                    email=email,
                    password=password_aleatoria,
                    first_name=nombre,
                    last_name=apellido,
                    id_rol_id=id_rol,
                    activo=activo,
                    plain_password=password_aleatoria
                )
                
                # Si hay una imagen, guardarla después de crear el usuario
                if imagen:
                    usuario.imagen = imagen
                    usuario.save()
                    
                print('Usuario creado y guardado exitosamente')
                
            except Exception as e:
                print(f'Error al guardar el usuario: {str(e)}')
                messages.error(request, f'Error al guardar el usuario: {str(e)}')
                return redirect('agregarUsuario')
            
        except KeyError as e:
            error_msg = f'Error: Campo faltante en el formulario - {str(e)}'
            print(error_msg)
            messages.error(request, error_msg)
            return redirect('agregarUsuario')
            
        except Exception as e:
            error_msg = f'Error inesperado: {str(e)}'
            print(error_msg)
            import traceback
            print(traceback.format_exc())  # Imprimir el traceback completo
            messages.error(request, 'Ocurrió un error al procesar la solicitud. Por favor, intente nuevamente.')
            return redirect('agregarUsuario')

        # Enviar la contraseña por correo electrónico
        try:
            send_mail(
                'Credenciales de acceso al Sistema de Votación de la Unidad Educativa Riobamba',
                f'Hola {nombre} {apellido},\n\nTus credenciales de acceso al sistema son las siguientes:\n\nUsuario (Cédula): {cedula}\nContraseña: {password_aleatoria}\n\nPor seguridad, te recomendamos cambiar tu contraseña después de iniciar sesión por primera vez.\n\nAtentamente,\nConsejo Electoral - Unidad Educativa Riobamba',
                'riobamba@aplicacionesutc.com',  # Remitente
                [email],
                fail_silently=True,  # Cambiado a True para que no falle si hay error en el envío
            )
            messages.success(request, 'Usuario creado exitosamente y credenciales enviadas por correo.')
        except Exception as e:
            error_msg = f'Usuario creado, pero ocurrió un error al enviar el correo: {str(e)}'
            print(error_msg)
            messages.warning(request, error_msg)
            messages.info(request, f'La contraseña generada es: {password_aleatoria}. Por favor, anótela y guárdela en un lugar seguro.')
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

#LOGIN

