from django.db import models
from django.core.exceptions import ValidationError
from Aplicaciones.periodo.models import Periodo
from django.utils import timezone

class Grado(models.Model):
    """Modelo para grados académicos (1ro, 2do, etc.)"""
    nombre = models.CharField(max_length=50)
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grados',
        verbose_name="Período académico"
    )

    class Meta:
        unique_together = ('nombre', 'periodo')
        ordering = ['nombre']
        verbose_name = "Grado"
        verbose_name_plural = "Grados"

    def __str__(self):
        return f"{self.nombre} ({self.periodo.nombre if self.periodo else 'Sin período'})"

class Paralelo(models.Model):
    """Modelo para paralelos (A, B, C) dentro de un grado"""
    nombre = models.CharField(max_length=5, verbose_name="Letra del paralelo")
    grado = models.ForeignKey(
        Grado, 
        on_delete=models.CASCADE, 
        related_name="paralelos",
        verbose_name="Grado asociado"
    )

    class Meta:
        unique_together = ('nombre', 'grado')
        ordering = ['grado', 'nombre']
        verbose_name = "Paralelo"
        verbose_name_plural = "Paralelos"

    def __str__(self):
        return f"{self.grado.nombre}-{self.nombre}"

class PadronElectoral(models.Model):
    """Modelo para el padrón electoral de estudiantes"""
    ESTADOS = [
        ('activo', 'Activo - Puede votar'),
        ('inactivo', 'Inactivo - No puede votar'),
    ]

    # Información personal
    cedula = models.CharField(max_length=10, unique=True, verbose_name="Cédula de identidad")
    nombre = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    correo = models.EmailField(verbose_name="Correo electrónico")
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono")
    
    # Relaciones académicas
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="padron_electoral",
        verbose_name="Período académico"
    )
    grado = models.ForeignKey(
        Grado,
        on_delete=models.CASCADE,
        verbose_name="Grado del estudiante"
    )
    paralelo = models.ForeignKey(
        Paralelo,
        on_delete=models.CASCADE,
        verbose_name="Paralelo del estudiante"
    )
    
    # Estado y fechas
    estado = models.CharField(
        max_length=10, 
        choices=ESTADOS, 
        default='activo',
        verbose_name="Estado en el padrón"
    )
    fecha_registro = models.DateTimeField(default=timezone.now, verbose_name="Fecha de registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        unique_together = [
            ('cedula', 'periodo'),  # Una cédula sólo puede estar una vez por período
            ('correo', 'periodo')   # Un correo sólo puede estar una vez por período
        ]
        verbose_name = "Registro electoral"
        verbose_name_plural = "Padrón electoral"
        ordering = ['apellidos', 'nombre']

    def __str__(self):
        return f"{self.apellidos} {self.nombre} - {self.grado.nombre}{self.paralelo.nombre}"

    def clean(self):
        """Validaciones para mantener la integridad de los datos"""
        # Verifica que el paralelo pertenezca al grado
        if self.paralelo.grado != self.grado:
            raise ValidationError("El paralelo seleccionado no corresponde al grado especificado")
        
        # Verifica que el grado pertenezca al período (si período existe)
        if self.periodo and self.grado.periodo != self.periodo:
            raise ValidationError("El grado seleccionado no corresponde al período especificado")