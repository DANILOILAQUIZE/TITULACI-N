from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo para los roles (tipos de usuario)
class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"

# Modelo de usuario vinculado a los roles
class Usuario(AbstractUser):
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    paralelo = models.CharField(max_length=10, blank=True, null=True)  # Para estudiantes
    grado = models.CharField(max_length=10, blank=True, null=True)     # Para estudiantes
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)

    # Solucionar el conflicto con related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_groups',  # Nombre único para el accessor inverso
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_permissions',  # Nombre único para el accessor inverso
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return f"{self.username} ({self.rol.nombre if self.rol else 'Sin rol'})"