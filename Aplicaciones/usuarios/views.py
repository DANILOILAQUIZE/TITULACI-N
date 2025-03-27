from django.shortcuts import render, redirect
from .models import Roles, Usuarios
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
# Create your views here.



def dashboard(request):
    return render(request, 'rol/dashboard.html')

#CREAMOS LAS VIEWS PARA LOS ROLES

def agregarrol(request):
    roles=Roles.objects.all()
    return render(request, 'rol/agregarrol.html.', {'roles': roles})

def guardarrol(request):
    nombre_rol=request.POST['nombre_rol']
    descripcion=request.POST['descripcion']
    Roles.objects.create(nombre_rol=nombre_rol, descripcion=descripcion)
    return redirect('agregarrol')

def listarroles(request):
    roles = Roles.objects.all()
    return render(request, 'rol/agregarrol.html', {'roles': roles})

def editarrol(request, rol_id):
    rol = get_object_or_404(Roles, id=rol_id)
    
    if request.method == 'POST':
        # Obtén los datos enviados en el formulario
        nombre_rol = request.POST.get('nombre_rol')
        descripcion = request.POST.get('descripcion', '')  # El campo descripcion es opcional
        
        # Verificar si el nombre del rol es válido
        if nombre_rol:
            rol.nombre_rol = nombre_rol
            rol.descripcion = descripcion
            rol.save()  # Guarda los cambios en la base de datos
            messages.success(request, 'Rol actualizado correctamente.')
            return redirect('listar_roles')  # Redirige después de la actualización
        else:
            messages.error(request, 'El nombre del rol es obligatorio.')
    
    # Si la solicitud no es POST, solo cargar los datos existentes
    return render(request, 'rol/editarrol.html', {'rol': rol})