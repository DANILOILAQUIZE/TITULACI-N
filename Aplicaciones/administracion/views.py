from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from Aplicaciones.padron.models import CredencialUsuario
from django.contrib.auth.hashers import check_password

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        # Redirigir a la página de inicio de sesión del padrón
        return render(request, 'index.html')
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def login_padron(request):
    # Log the incoming request data for debugging
    print("\n=== INICIO DE SOLICITUD DE INICIO DE SESIÓN ===")
    print(f"Método: {request.method}")
    print(f"POST data: {request.POST}")
    print(f"Headers: {request.headers}")
    
    # Verificar el token CSRF
    if not request.META.get('CSRF_COOKIE'):
        print("Error: No se encontró el token CSRF en las cookies")
        return JsonResponse({
            'success': False,
            'message': 'Error de seguridad. Por favor, recargue la página e intente nuevamente.'
        }, status=403)
    
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    
    if not username or not password:
        print(f"Error: Usuario o contraseña vacíos. Usuario: '{username}', Contraseña: {'*' * len(password)}")
        return JsonResponse({
            'success': False,
            'message': 'Por favor ingrese su cédula y contraseña'
        }, status=400)
    
    try:
        print(f"Buscando credencial para el usuario: {username}")
        # Buscar la credencial del usuario (sin filtrar por estado primero)
        try:
            credencial = CredencialUsuario.objects.get(usuario=username)
            print(f"Credencial encontrada: {credencial}")
            
            # Verificar si la cuenta está activa
            if credencial.estado != 'activo':
                print(f"Error: La cuenta del usuario {username} no está activa. Estado actual: {credencial.estado}")
                return JsonResponse({
                    'success': False,
                    'message': 'Su cuenta no está activa. Por favor, contacte al administrador.'
                }, status=400)
                
            # Verificar la contraseña
            print(f"[DEBUG] Iniciando verificación de contraseña para usuario: {username}")
            print(f"[DEBUG] Contraseña proporcionada: {password}")
            print(f"[DEBUG] Contraseña encriptada almacenada: {credencial.contrasena_encriptada}")
            print(f"[DEBUG] Contraseña en texto plano: {credencial._contrasena_plana if hasattr(credencial, '_contrasena_plana') else 'No disponible'}")
            
            from django.contrib.auth.hashers import check_password
            print(f"[DEBUG] Usando check_password directamente: {check_password(password, credencial.contrasena_encriptada)}")
            
            if not credencial.verificar_contrasena(password):
                print(f"[ERROR] La verificación de contraseña falló para el usuario {username}")
                print(f"[DEBUG] Detalles de la credencial: {credencial.__dict__}")
                return JsonResponse({
                    'success': False,
                    'message': 'Cédula o contraseña incorrectos'
                }, status=400)
                
        except CredencialUsuario.DoesNotExist:
            print(f"Error: No se encontró el usuario {username}")
            # No revelamos que el usuario no existe por seguridad
            return JsonResponse({
                'success': False,
                'message': 'Cédula o contraseña incorrectos'
            }, status=400)
        
        # Verificar si ya votó
        if hasattr(credencial.padron, 'voto') and credencial.padron.voto:
            print(f"Usuario {username} intentó votar nuevamente - Voto ya emitido")
            return JsonResponse({
                'success': False,
                'message': 'Usted ya ha emitido su voto para este proceso electoral. No puede votar nuevamente.',
                'voto_ya_emitido': True
            }, status=400)
        
        # Iniciar sesión manualmente
        from django.contrib.auth import get_user_model
        from django.contrib.auth import login as auth_login
        
        User = get_user_model()
        
        # Intentar obtener el usuario existente o crearlo con un correo único
        try:
            user = User.objects.get(username=credencial.usuario)
        except User.DoesNotExist:
            # Crear un correo único basado en el nombre de usuario si no existe
            email = f"{credencial.usuario}@sistema-voto.com"
            user = User.objects.create_user(
                username=credencial.usuario,
                email=email,
                password=None,  # No necesitamos contraseña ya que usamos autenticación personalizada
                is_active=True
            )
        
        if user:
            auth_login(request, user)
            # Guardar el ID del padrón en la sesión
            request.session['padron_id'] = credencial.padron.id
            
            # Obtener el proceso electoral activo
            from Aplicaciones.votacion.models import ProcesoElectoral
            try:
                proceso_activo = ProcesoElectoral.objects.get(estado='activo')
                redirect_url = f'/votacion/papeleta/{proceso_activo.id}/'
            except ProcesoElectoral.DoesNotExist:
                # Si no hay proceso activo, redirigir a una página de error
                return JsonResponse({
                    'success': False,
                    'message': 'No hay un proceso electoral activo en este momento.'
                }, status=400)
            
            return JsonResponse({
                'success': True,
                'redirect_url': redirect_url
            })
            
    except CredencialUsuario.DoesNotExist as e:
        print(f"Error: No se encontró el usuario o la cuenta no está activa - {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Cédula o contraseña incorrectos',
            'error': 'Credencial no encontrada o inactiva'
        }, status=400)
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': 'Ocurrió un error al procesar la solicitud',
            'error': str(e)
        }, status=500)



@login_required
def logout_padron(request):
    auth_logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('administracion:index')

@login_required
def dashboard(request):
    return render(request, 'rol/dashboard.html')

def plantilla(request):
    return render(request, 'administracion/plantilla.html')

def mision_vision(request):
    return render(request, 'administracion/mision_vision.html')

def nosotros(request):
    return render(request, 'administracion/nosotros.html')

def docentes(request):
    return render(request, 'administracion/docentes.html')

def docentes_nuevo(request):
    return render(request, 'administracion/docentes-nuevo.html')

def noticias(request):
    return render(request, 'administracion/noticias.html')


