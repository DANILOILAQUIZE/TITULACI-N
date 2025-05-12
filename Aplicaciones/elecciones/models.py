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
    color = models.CharField(max_length=20, default='azul', help_text='Color representativo de la lista (nombre o código hexadecimal)')

    def __str__(self):
        return f"{self.nombre_lista} ({self.periodo.nombre})"
    

class Cargo(models.Model):
    
    nombre_cargo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)  
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.get_nombre_cargo_display()} ({self.periodo.nombre})"
    
class Candidato(models.Model):
    nombre_candidato = models.CharField(max_length=100) 
    lista = models.ForeignKey(Lista, on_delete=models.CASCADE)  
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE) 
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE) 
    padron=models.ForeignKey(PadronElectoral, on_delete=models.CASCADE, null=True, blank=True)
    imagen = models.ImageField(upload_to='candidatos/', null=True, blank=True)  

    def __str__(self):
        return f"{self.nombre_candidato} - {self.cargo.nombre_cargo} ({self.lista.nombre_lista})"