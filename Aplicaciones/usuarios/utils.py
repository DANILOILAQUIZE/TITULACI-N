import hashlib
import random

def get_random_color(string):
    """Genera un color único basado en el string proporcionado"""
    hash_object = hashlib.md5(string.encode())
    hex_dig = hash_object.hexdigest()
    
    # Usar solo colores con suficiente saturación y luminosidad
    r = int(hex_dig[0:2], 16) % 200 + 30  # Rango: 30-230
    g = int(hex_dig[2:4], 16) % 200 + 30  # Rango: 30-230
    b = int(hex_dig[4:6], 16) % 200 + 30  # Rango: 30-230
    
    return f"rgb({r}, {g}, {b})"

def get_contrast_color(rgb_color):
    """Determina si el color es claro u oscuro para elegir el color del texto"""
    # Extraer valores RGB del string
    rgb_values = rgb_color.replace('rgb(', '').replace(')', '').split(',')
    r, g, b = map(int, rgb_values)
    
    # Calcular luminosidad (fórmula de percepción humana)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    # Devolver blanco o negro con diferente opacidad para mejor contraste
    if luminance < 0.5:
        return 'rgba(255, 255, 255, 0.95)'  # Blanco con 95% de opacidad
    else:
        return 'rgba(0, 0, 0, 0.85)'  # Negro con 85% de opacidad

def generate_avatar_svg(user, size=48, font_size=20):
    """Genera un avatar SVG con las iniciales del usuario y un diseño moderno"""
    # Obtener las iniciales (primera letra del nombre y primera del apellido)
    initials = (user.nombre[0] + (user.apellido[0] if user.apellido else ''))[:2].upper()
    
    # Generar colores únicos basados en el nombre de usuario
    color1 = get_random_color(user.username + '1')
    color2 = get_random_color(user.username + '2')
    text_color = get_contrast_color(color1)
    
    # Elegir aleatoriamente entre diferentes estilos de avatar
    style = random.choice(['gradient', 'solid', 'pattern'])
    
    # Crear el SVG del avatar con diseño mejorado
    if style == 'gradient':
        # Estilo con degradado
        svg = f'''
        <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:{color1};stop-opacity:1" />
                    <stop offset="100%" style="stop-color:{color2};stop-opacity:0.8" />
                </linearGradient>
                <filter id="dropShadow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur in="SourceAlpha" stdDeviation="2" result="blur" />
                    <feOffset in="blur" dx="1" dy="1" result="offsetBlur" />
                    <feMerge>
                        <feMergeNode in="offsetBlur" />
                        <feMergeNode in="SourceGraphic" />
                    </feMerge>
                </filter>
            </defs>
            <circle cx="{size//2}" cy="{size//2}" r="{size//2 - 2}" fill="url(#grad1)" filter="url(#dropShadow)" />
            <text x="50%" y="55%" font-family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif" 
                  font-size="{font_size}" font-weight="600" letter-spacing="0.5"
                  fill="{text_color}" text-anchor="middle" dominant-baseline="middle"
                  style="text-shadow: 0 1px 2px rgba(0,0,0,0.2);">
                {initials}
            </text>
        </svg>
        '''
    elif style == 'pattern':
        # Estilo con patrón geométrico
        svg = f'''
        <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="pattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                    <path d="M 10,10 L 15,10 L 15,15 L 10,15 Z" fill="{color1}" fill-opacity="0.7" />
                    <path d="M 0,0 L 5,0 L 5,5 L 0,5 Z" fill="{color2}" fill-opacity="0.7" />
                </pattern>
            </defs>
            <circle cx="{size//2}" cy="{size//2}" r="{size//2 - 2}" fill="{color1}" />
            <circle cx="{size//2}" cy="{size//2}" r="{size//2 - 4}" fill="url(#pattern)" />
            <text x="50%" y="55%" font-family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif" 
                  font-size="{font_size}" font-weight="600"
                  fill="{text_color}" text-anchor="middle" dominant-baseline="middle"
                  style="text-shadow: 0 1px 2px rgba(0,0,0,0.2);">
                {initials}
            </text>
        </svg>
        '''
    else:
        # Estilo sólido con borde
        svg = f'''
        <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="borderGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:{color1};stop-opacity:1" />
                    <stop offset="100%" style="stop-color:{color2};stop-opacity:0.8" />
                </linearGradient>
            </defs>
            <rect x="2" y="2" width="{size-4}" height="{size-4}" rx="12" 
                  fill="{color1}" stroke="url(#borderGradient)" stroke-width="2" />
            <text x="50%" y="55%" font-family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif" 
                  font-size="{font_size}" font-weight="600"
                  fill="{text_color}" text-anchor="middle" dominant-baseline="middle"
                  style="text-shadow: 0 1px 2px rgba(0,0,0,0.2);">
                {initials}
            </text>
        </svg>
        '''
    
    # Convertir el SVG a data-uri
    from urllib.parse import quote
    svg_encoded = quote(svg.replace('\n', '').replace('    ', ''))
    return f'data:image/svg+xml;utf8,{svg_encoded}'
