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

    def verificar_contrasena(self, contrasena):
        """Verifica si la contraseña proporcionada coincide con la almacenada"""
        from django.contrib.auth.hashers import check_password
        return check_password(contrasena, self.get_contrasena_encriptada())


class CredencialUsuario(models.Model):
    """Modelo para almacenar las credenciales de los usuarios del sistema"""
    padron = models.OneToOneField(
        PadronElectoral,
        on_delete=models.CASCADE,
        related_name='credencial',
        verbose_name="Registro del padrón"
    )
    
    # Usuario será la cédula del estudiante
    usuario = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Nombre de usuario"
    )
    
    # Contraseña encriptada
    contrasena = models.CharField(
        max_length=128,
        verbose_name="Contraseña"
    )
    
    fecha_generacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de generación"
    )
    
    # Estado de la credencial
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('cambiada', 'Contraseña cambiada')
    ]
    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default='activo',
        verbose_name="Estado de la credencial"
    )
    
    class Meta:
        verbose_name = "Credencial de usuario"
        verbose_name_plural = "Credenciales de usuarios"
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"{self.padron.cedula} - {self.padron.nombre} {self.padron.apellidos}"

    def cambiar_estado(self, nuevo_estado):
        """Cambia el estado de la credencial"""
        if nuevo_estado in dict(self.ESTADOS):
            self.estado = nuevo_estado
            self.save()
            return True
        return False

    def cambiar_contrasena(self, nueva_contrasena):
        """Cambia la contraseña y actualiza el estado"""
        self.contrasena = nueva_contrasena
        self.estado = 'cambiada'
        self.save()
        return True

    def generar_contrasena(self):
        """Genera una nueva contraseña aleatoria"""
        import random
        import string
        nueva_contrasena = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.contrasena = nueva_contrasena
        self.save()
        return nueva_contrasena

    @property
    def get_contrasena_plana(self):
        """Devuelve la contraseña en texto plano (sólo para mostrar)"""
        # La contraseña se almacena en texto plano en la base de datos
        return str(self.contrasena)

    def get_contrasena_encriptada(self):
        """Devuelve la contraseña encriptada"""
        from django.contrib.auth.hashers import make_password
        return make_password(self.contrasena)

    def verificar_contrasena(self, contrasena):
        """Verifica si la contraseña proporcionada coincide con la almacenada"""
        from django.contrib.auth.hashers import check_password
        return check_password(contrasena, self.get_contrasena_encriptada())

# Importar después de definir los modelos para evitar errores de importación circular
from django.contrib.auth.hashers import make_password, check_password

# Validaciones adicionales
from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=CredencialUsuario)
def validar_credencial(sender, instance, **kwargs):
    """Validaciones adicionales antes de guardar una credencial"""
    # Verificar que el usuario (cedula) sea único
    if CredencialUsuario.objects.filter(usuario=instance.usuario).exclude(id=instance.id).exists():
        raise ValidationError('Ya existe una credencial con este usuario')
    
    # Solo encriptar la contraseña si no es una nueva generación
    if not instance.pk and not instance.contrasena.startswith('pbkdf2_sha256$'):
        instance.contrasena = make_password(instance.contrasena)