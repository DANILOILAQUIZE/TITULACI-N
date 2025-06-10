from django.contrib import admin
from .models import Grado, Paralelo, PadronElectoral, CredencialUsuario

# Register your models here.
admin.site.register(Grado)
admin.site.register(Paralelo)
admin.site.register(PadronElectoral)
admin.site.register(CredencialUsuario)