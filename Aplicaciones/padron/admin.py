from django.contrib import admin
from .models import Grado, Paralelo, PadronElectoral
# Register your models here.
admin.site.register(Grado,)
admin.site.register(Paralelo,)
admin.site.register(PadronElectoral)