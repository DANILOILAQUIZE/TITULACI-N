from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.hashers import make_password
from .models import Grado, Paralelo, PadronElectoral, CredencialUsuario

@admin.register(CredencialUsuario)
class CredencialUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'get_padron_nombre', 'get_contrasena_plana_display', 'estado', 'fecha_generacion')
    search_fields = ('usuario', 'padron__nombre', 'padron__apellidos')
    list_filter = ('estado', 'fecha_generacion')
    readonly_fields = ('fecha_generacion', 'get_contrasena_plana_display')
    
    def get_readonly_fields(self, request, obj=None):
        """Hace que la contraseña sea de solo lectura si ya existe"""
        if obj and obj._contrasena_plana:
            return self.readonly_fields + ('contrasena',)
        return self.readonly_fields
    
    def get_form(self, request, obj=None, **kwargs):
        """Personaliza el formulario para manejar la contraseña"""
        form = super().get_form(request, obj, **kwargs)
        
        # Si el objeto ya tiene una contraseña, la hacemos de solo lectura
        if obj and obj._contrasena_plana:
            form.base_fields['contrasena'].help_text = 'Ya existe una contraseña generada. Para cambiarla, contacte a un administrador.'
        else:
            form.base_fields['contrasena'].help_text = 'Deje este campo en blanco para generar una contraseña automática'
            
        return form
    
    def get_contrasena_plana_display(self, obj):
        """Muestra la contraseña en texto plano solo si está disponible"""
        if obj._contrasena_plana:
            return '••••••••'  # Muestra 8 puntos como indicador de contraseña
        return "No generada"
    get_contrasena_plana_display.short_description = 'Contraseña'
    
    def get_padron_nombre(self, obj):
        return f"{obj.padron.nombre} {obj.padron.apellidos}"
    get_padron_nombre.short_description = 'Estudiante'
    get_padron_nombre.admin_order_field = 'padron__apellidos'
    
    def save_model(self, request, obj, form, change):
        """
        Asegura que la contraseña se guarde correctamente.
        Solo genera una nueva contraseña si no existe una previamente.
        """
        # Si es una edición, obtener el objeto actual de la base de datos
        if change and obj.pk:
            try:
                obj_actual = CredencialUsuario.objects.get(pk=obj.pk)
                # Si la contraseña no ha cambiado, mantener la existente
                if not form.changed_data or 'contrasena' not in form.changed_data:
                    obj._contrasena_plana = obj_actual._contrasena_plana
            except CredencialUsuario.DoesNotExist:
                pass
        
        # Si no hay contraseña en texto plano, generar una automáticamente
        if not obj._contrasena_plana:
            obj.generar_contrasena()
        
        # Guardar la contraseña en texto plano temporalmente
        contrasena_plana = obj._contrasena_plana
        
        # Si la contraseña parece estar encriptada, generar una nueva
        if (isinstance(contrasena_plana, str) and 
            (contrasena_plana.startswith('pbkdf2_sha256$') or 
             contrasena_plana.startswith('bcrypt$') or
             len(contrasena_plana) > 50)):
            contrasena_plana = obj.generar_contrasena()
        
        # Llamar al save del modelo para que se encargue de la encriptación
        super().save_model(request, obj, form, change)
        
        # Actualizar solo el campo _contrasena_plana con el valor correcto
        CredencialUsuario.objects.filter(pk=obj.pk).update(_contrasena_plana=contrasena_plana)

# Registro de los modelos restantes
admin.site.register(Grado)
admin.site.register(Paralelo)
admin.site.register(PadronElectoral)