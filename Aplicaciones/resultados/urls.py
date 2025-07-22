from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

# Función para aplicar login_required a las vistas basadas en funciones
def login_required_view(view_func):
    return login_required(view_func, login_url='login')

urlpatterns = [
    # Rutas de resultados (requieren autenticación)
    path('proceso/<int:proceso_id>/', login_required_view(views.resultados_votacion), name='resultados_votacion'),
    path('lista/', login_required_view(views.lista_resultados), name='lista_resultados'),
]
