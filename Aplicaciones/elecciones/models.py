from django.db import models
from Aplicaciones.periodo.models import Periodo
from Aplicaciones.padron.models import PadronElectoral
# Create your models here.
#MODELS PARA AGREGAR LISTAS, CARGOS, CANDIDATOS

class Lista(models.Model):
    nombre_lista = models.CharField(max_length=100) 
    frase = models.CharField(max_length=255, null=True, blank=True)  
    imagen = models.ImageField(upload_to='listas/', null=True, blank=True)  
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)  

    def __str__(self):
        return f"{self.nombre_lista} ({self.periodo.nombre})"
    

class Cargo(models.Model):
    
    nombre_cargo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)  
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.get_nombre_cargo_display()} ({self.periodo.nombre})"
    
class Candidato(models.Model):
    nombre_candidato = models.CharField(max_length=100)  # Nombre del candidato
    lista = models.ForeignKey(Lista, on_delete=models.CASCADE)  # Relación con la lista a la que pertenece
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)  # Relación con el cargo que ocupa (Presidente, Vicepresidente, etc.)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)  # Relación con el periodo electoral
    imagen = models.ImageField(upload_to='candidatos/', null=True, blank=True)  # Imagen del candidato (opcional)

    def __str__(self):
        return f"{self.nombre_candidato} - {self.cargo.nombre_especifico} ({self.lista.nombre_lista})"