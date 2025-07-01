import qrcode
import hashlib
import os
from io import BytesIO
from django.core.files import File
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime
from premailer import transform

def generar_codigo_verificacion(voto):
    """
    Genera un código de verificación único para el voto
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    texto = f"{voto.id}-{voto.votante.cedula}-{timestamp}"
    return hashlib.sha256(texto.encode()).hexdigest()

def generar_carnet_votacion(voto):
    """
    Genera un carnet de votación para un voto emitido
    """
    import qrcode
    from .models import CarnetVotacion
    from django.core.files.base import ContentFile
    import base64
    
    # Generar código de verificación
    codigo_verificacion = generar_codigo_verificacion(voto)
    
    # Crear el registro del carnet
    carnet = CarnetVotacion(
        voto=voto,
        codigo_verificacion=codigo_verificacion,
        nombre_completo=f"{voto.votante.nombre} {voto.votante.apellidos}",
        cedula=voto.votante.cedula,
        proceso_electoral=str(voto.proceso_electoral),
        fecha_votacion=voto.fecha_voto
    )
    
    # Generar código QR con la información del voto
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Crear el contenido del QR con la información del voto
    qr_data = f"""
    SISTEMA DE VOTACIÓN UE RIOBAMBA
    ------------------------------
    Proceso: {voto.proceso_electoral}
    Cédula: {voto.votante.cedula}
    Nombre: {voto.votante.nombre} {voto.votante.apellidos}
    Fecha: {voto.fecha_voto.strftime('%d/%m/%Y %H:%M:%S')}
    Código: {codigo_verificacion}
    ------------------------------
    Este es un comprobante de votación electrónica
    """
    
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Crear la imagen del QR
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar la imagen del QR en un buffer
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    
    # Convertir la imagen a base64 para mostrarla en el HTML
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Guardar el carnet con la imagen del QR en base64
    carnet.codigo_qr = f"data:image/png;base64,{qr_base64}"
    carnet.save()
    
    # Enviar comprobante por correo electrónico
    enviar_comprobante_email(carnet)
    
    return carnet


def enviar_comprobante_email(carnet):
    """
    Envía el comprobante de votación por correo electrónico al votante
    """
    try:
        from django.core.mail import send_mail
        
        # Obtener el correo del votante
        email_destino = carnet.voto.votante.correo
        
        if not email_destino:
            print("No se encontró correo electrónico para el votante")
            return False
            
        print(f'=== ENVIANDO COMPROBANTE A: {email_destino} ===')
        
        # Renderizar el template HTML del correo
        context = {
            'carnet': carnet,
            'fecha_votacion': carnet.fecha_votacion.strftime("%d/%m/%Y %H:%M"),
        }
        
        # Renderizar el contenido del correo
        html_content = render_to_string('votacion/email_comprobante.html', context)
        
        # Crear versión de texto plano
        text_content = strip_tags(html_content)
        
        # Configurar el asunto
        subject = f'Comprobante de Votación - {carnet.proceso_electoral}'
        
        # Enviar el correo usando la misma configuración que en el módulo de padrón
        send_mail(
            subject,
            text_content,
            'riobamba@aplicacionesutc.com',  # Usando el mismo remitente que en el módulo de padrón
            [email_destino],
            html_message=html_content,
            fail_silently=False
        )
        
        print('Correo enviado exitosamente')
        return True
        
    except Exception as e:
        import traceback
        print('=== ERROR AL ENVIAR CORREO ===')
        print(f'Tipo de error: {type(e).__name__}')
        print(f'Mensaje de error: {str(e)}')
        print('Traceback:')
        print(traceback.format_exc())
        print('=== FIN DEL ERROR ===')
        return False
