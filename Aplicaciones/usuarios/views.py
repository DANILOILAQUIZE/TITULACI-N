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