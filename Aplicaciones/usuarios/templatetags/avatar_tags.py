from django import template
from django.templatetags.static import static
import hashlib
import random

register = template.Library()

def get_random_color(string):
    """Genera un color único basado en el string proporcionado"""
    # Usar hash para generar un color consistente
    hash_object = hashlib.md5(string.encode())
    hex_dig = hash_object.hexdigest()
    # Tomar los primeros 6 caracteres del hash para el color
    return f"#{hex_dig[:6]}"

def get_contrast_color(hex_color):
    """Determina si el color es claro u oscuro para elegir el color del texto"""
    # Convertir el color hex a RGB
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    # Calcular luminosidad (fórmula de percepción humana)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return '#ffffff' if luminance < 0.5 else '#000000'

@register.simple_tag
def user_avatar(user, size=40, font_size=16):
    """Genera un avatar con las iniciales del usuario sobre un fondo de color"""
    # Obtener las iniciales (primera letra del nombre y primera del apellido)
    initials = (user.nombre[0] + (user.apellido[0] if user.apellido else ''))[:2].upper()
    
    # Generar un color único basado en el nombre de usuario
    bg_color = get_random_color(user.username)
    text_color = get_contrast_color(bg_color)
    
    # Crear el SVG del avatar
    svg = f'''
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
        <rect width="{size}" height="{size}" rx="4" fill="{bg_color}"/>
        <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="{font_size}" 
              fill="{text_color}" text-anchor="middle" dominant-baseline="middle">
            {initials}
        </text>
    </svg>
    '''
    
    # Convertir el SVG a data-uri para usarlo como imagen
    from urllib.parse import quote
    svg_encoded = quote(svg.replace('\n', '').replace('    ', ''))
    return f'data:image/svg+xml;utf8,{svg_encoded}'
