from django import template
from ..utils import generate_avatar_svg

register = template.Library()

@register.simple_tag
def user_avatar(user, size=40):
    """Template tag para generar un avatar SVG para el usuario"""
    return generate_avatar_svg(user, size=size)
