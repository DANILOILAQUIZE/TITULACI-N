from django.contrib import admin

# Register your models here.
from.models import PadrónElectoral

@admin.register(PadrónElectoral)
class PadrónElectoralAdmin(admin.ModelAdmin):
    list_display = ('cedula', 'nombre', 'apellidos', 'grado', 'paralelo')
    search_fields = ('cedula', 'nombre', 'apellidos')
    list_filter = ('grado', 'paralelo', 'estado')