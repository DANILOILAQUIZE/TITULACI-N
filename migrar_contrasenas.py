"""
Script para migrar contraseñas existentes al nuevo formato.

Este script actualiza todas las contraseñas existentes en la base de datos
al nuevo formato que incluye encriptación segura.
"""
import os
import sys
import django

# Configurar el entorno de Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_voto_ue_riobamba.settings')
django.setup()

from Aplicaciones.padron.models import CredencialUsuario
from django.contrib.auth.hashers import make_password

def migrar_contraseñas():
    """Migra todas las contraseñas al nuevo formato encriptado."""
    credenciales = CredencialUsuario.objects.all()
    actualizadas = 0
    
    for credencial in credenciales:
        # Si ya tiene contraseña encriptada, saltar
        if credencial.contrasena_encriptada:
            continue
            
        # Si tiene contraseña en texto plano, encriptarla
        if credencial._contrasena_plana:
            credencial.contrasena_encriptada = make_password(credencial._contrasena_plana)
            credencial.save(update_fields=['contrasena_encriptada'])
            actualizadas += 1
    
    return actualizadas

if __name__ == "__main__":
    print("Iniciando migración de contraseñas...")
    total_actualizadas = migrar_contraseñas()
    print(f"Migración completada. Se actualizaron {total_actualizadas} contraseñas.")
