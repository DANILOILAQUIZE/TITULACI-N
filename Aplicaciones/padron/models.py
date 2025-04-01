from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
Usuarios = get_user_model()  # Obtiene el modelo personalizado de usuario

class Grado(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  

    def __str__(self):
        return self.nombre

class Paralelo(models.Model):
    nombre = models.CharField(max_length=5)  # Ejemplo: "A", "B"
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name="paralelos")

    def __str__(self):
        return f"{self.grado} - {self.nombre}"

class PadrónElectoral(models.Model):
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    # Cambiar a null=True, blank=True para hacerlo opcional
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Usa AUTH_USER_MODEL en lugar del modelo directo
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Usuario del sistema"
    )
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE, null=True, blank=True)
    cedula = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE, related_name="estudiantes")
    paralelo = models.ForeignKey(Paralelo, on_delete=models.CASCADE, related_name="estudiantes")
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo')

    usuario_temp = models.CharField(max_length=50, blank=True, null=True)  # Para almacenar el nombre de usuario
    contraseña_temp = models.CharField(max_length=50, blank=True, null=True) 
    def __str__(self):
        return f"{self.nombre} {self.apellidos}"