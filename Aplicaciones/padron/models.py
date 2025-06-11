from django.db import models
from django.core.exceptions import ValidationError
from Aplicaciones.periodo.models import Periodo
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.db.models.signals import pre_save
from django.dispatch import receiver

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
    
    # Contraseña encriptada (se almacena encriptada, pero se puede acceder a la versión en texto plano)
    _contrasena_plana = models.CharField(
        max_length=128,
        verbose_name="Contraseña (texto plano)",
        blank=True,
        null=True,
        help_text="Se almacena temporalmente para mostrarla al administrador"
    )
    contrasena_encriptada = models.CharField(
        max_length=128,
        verbose_name="Contraseña (encriptada)",
        blank=True,
        null=True
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

    def generar_contrasena(self, forzar=False):
        """
        Genera una nueva contraseña aleatoria solo si no existe una previamente
        
        Args:
            forzar (bool): Si es True, genera una nueva contraseña incluso si ya existe una
        """
        # Si ya existe una contraseña y no se está forzando, retornar la existente
        if not forzar and self._contrasena_plana:
            return self._contrasena_plana
            
        import random
        import string
        
        # Generar una contraseña segura con mayúsculas, minúsculas y números
        caracteres = string.ascii_letters + string.digits
        while True:
            nueva_contrasena = ''.join(random.choices(caracteres, k=8))
            # Asegurarse de que tenga al menos un número, una mayúscula y una minúscula
            if (any(c.isdigit() for c in nueva_contrasena) and 
                any(c.isupper() for c in nueva_contrasena) and
                any(c.islower() for c in nueva_contrasena)):
                break
                
        # Guardar la contraseña (se encriptará automáticamente)
        self.contrasena = nueva_contrasena
        # Solo establecer como 'activo' si es una nueva cuenta
        if not self.pk:
            self.estado = 'activo'
        self.save()
        return nueva_contrasena

    @property
    def contrasena(self):
        """Propiedad para compatibilidad con código existente"""
        return self._contrasena_plana or ''

    @contrasena.setter
    def contrasena(self, value):
        """Setter para guardar tanto la versión en texto plano como la encriptada"""
        if value:  # Solo actualizar si se proporciona un valor
            self._contrasena_plana = value
            self.contrasena_encriptada = make_password(value)
    
    @property
    def get_contrasena_plana(self):
        """
        Devuelve la contraseña en texto plano si está disponible.
        Si no hay contraseña en texto plano, devuelve una cadena vacía.
        """
        # Si _contrasena_plana es None o está vacío, devolvemos cadena vacía
        if not self._contrasena_plana:
            # Si tenemos la contraseña encriptada pero no en texto plano, 
            # no podemos recuperar la contraseña original
            return ""
        
        # Si parece ser una contraseña encriptada, no la devolvemos
        if (isinstance(self._contrasena_plana, str) and 
            (self._contrasena_plana.startswith('bcrypt$') or 
             self._contrasena_plana.startswith('pbkdf2_sha256$') or
             len(self._contrasena_plana) > 50)):  # Las contraseñas encriptadas suelen ser largas
            return ""
            
        # Si llegamos aquí, es una contraseña en texto plano válida
        return self._contrasena_plana

    def get_contrasena_encriptada(self):
        """Devuelve la contraseña encriptada"""
        if not self.contrasena_encriptada and self._contrasena_plana:
            self.contrasena_encriptada = make_password(self._contrasena_plana)
            self.save(update_fields=['contrasena_encriptada'])
        return self.contrasena_encriptada

    def save(self, *args, **kwargs):
        # Si se está actualizando una instancia existente
        if self.pk:
            # Obtener la instancia actual de la base de datos
            old_instance = CredencialUsuario.objects.get(pk=self.pk)
            
            # Si la contraseña en texto plano no ha cambiado, mantener la encriptada existente
            if (self._contrasena_plana == old_instance._contrasena_plana and 
                old_instance.contrasena_encriptada):
                self.contrasena_encriptada = old_instance.contrasena_encriptada
            # Si la contraseña en texto plano ha cambiado, actualizar la encriptada
            elif self._contrasena_plana:
                self.contrasena_encriptada = make_password(self._contrasena_plana)
        # Si es una nueva instancia y hay contraseña en texto plano, encriptarla
        elif self._contrasena_plana:
            self.contrasena_encriptada = make_password(self._contrasena_plana)
        
        # Validar que la contraseña en texto plano no esté encriptada
        if (self._contrasena_plana and 
            isinstance(self._contrasena_plana, str) and 
            (self._contrasena_plana.startswith('bcrypt$') or 
             self._contrasena_plana.startswith('pbkdf2_sha256$'))):
            # Si parece estar encriptada, limpiar el campo
            self._contrasena_plana = ""
            
        # Llamar al save del padre
        super().save(*args, **kwargs)

    def verificar_contrasena(self, contrasena):
        """Verifica si la contraseña proporcionada coincide con la almacenada"""
        # Obtener la contraseña encriptada
        contrasena_encriptada = self.get_contrasena_encriptada()
        
        # Si no hay contraseña encriptada, verificar contra la versión en texto plano
        if not contrasena_encriptada and self._contrasena_plana:
            return contrasena == self._contrasena_plana
            
        # Verificar la contraseña usando el método seguro de Django
        return check_password(contrasena, contrasena_encriptada)

@receiver(pre_save, sender=CredencialUsuario)
def validar_credencial(sender, instance, **kwargs):
    """Validaciones adicionales antes de guardar una credencial"""
    # Verificar que el usuario (cedula) sea único
    if CredencialUsuario.objects.filter(usuario=instance.usuario).exclude(id=instance.id).exists():
        raise ValidationError('Ya existe una credencial con este usuario')
    
    # Solo encriptar la contraseña si no es una nueva generación
    if not instance.pk and not instance.contrasena.startswith('pbkdf2_sha256$'):
        instance.contrasena = make_password(instance.contrasena)