from django.db import models
from django.contrib.auth.models import AbstractUser

class Roles(models.Model):
    nombre_rol = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)  # Descripción opcional del rol
   
    def __str__(self):
        return self.nombre_rol

class Usuarios(AbstractUser):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, null=True, blank=True)  # Hacer nullable
    email = models.EmailField(unique=True)
    id_rol = models.ForeignKey(Roles, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    imagen = models.ImageField(upload_to='perfil_imagenes/', null=True, blank=True)  # Nuevo campo de imagen

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nombre', 'apellido']

    def __str__(self):
        return f"{self.nombre} {self.apellido or 'Sin apellido'}"