from django.db import models
from datetime import date
# Create your models here.
class Periodo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    def __str__(self):
        return self.nombre
    
    @property
    def estado(self):
        hoy = date.today()
        if hoy < self.fecha_inicio:
            return 'Pendiente'
        elif self.fecha_inicio <= hoy <= self.fecha_fin:
            return 'Activo'
        else:
            return 'Finalizado'

    @property
    def duracion(self):
        return (self.fecha_fin - self.fecha_inicio).days