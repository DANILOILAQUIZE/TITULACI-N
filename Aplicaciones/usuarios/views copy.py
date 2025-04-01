from django.shortcuts import render, redirect
from .models import Roles, Usuarios
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
# Create your views here.



def dashboard(request):
    return render(request, 'rol/dashboard.html')

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

# Vista para guardar el usuario
def guardarUsuario(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        id_rol = request.POST['id_rol']
        activo = request.POST.get('activo', 'off') == 'on'
        imagen = request.FILES.get('imagen')  # Obtener la imagen del formulario

        # Verificar si el username ya está en uso
        if Usuarios.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso. Por favor, elige otro.')
            return redirect('agregarUsuario')

        # Crear el usuario
        usuario = Usuarios(
            nombre=nombre,
            apellido=apellido,
            email=email,
            username=username,
            password=make_password(password),
            id_rol_id=id_rol,
            activo=activo,
            imagen=imagen
        )
        usuario.save()

        messages.success(request, 'Usuario agregado con éxito.')
        return redirect('agregarUsuario')  # Volver a la lista de usuarios

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

    # Si el usuario está activo, desactivarlo, sino no hacer nada
    if usuario.activo:
        usuario.activo = False  # Cambiar el estado a desactivado
        usuario.save()
        messages.success(request, "Usuario desactivado con éxito.")
    else:
        messages.info(request, "El usuario ya está desactivado.")
    
    # Redirigir a la vista de usuarios
    return redirect('agregarUsuario')