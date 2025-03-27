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

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido or 'Sin apellido'}"