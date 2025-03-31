from django.db import models
from django.contrib.auth.models import AbstractUser

class Roles(models.Model):
    nombre_rol = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre_rol

class Usuarios(AbstractUser):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    id_rol = models.ForeignKey('Roles', on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='perfil/', blank=True, null=True)

    USERNAME_FIELD = 'email'  # Usar email para autenticación
    REQUIRED_FIELDS = ['username', 'nombre']  # Campos adicionales requeridos

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios'

    def __str__(self):
        return f"{self.nombre} {self.apellido or ''}"