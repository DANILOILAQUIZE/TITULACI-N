import re

# Ruta al archivo original
file_path = r"c:\TITULACIÓN\sistema_voto_ue_riobamba\Aplicaciones\votacion\views.py"

# Leer el contenido del archivo
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Patrón para encontrar la sección que necesitamos modificar
pattern = r'(# Obtener la información del padrón\n\s+from Aplicaciones\.padron\.models import PadronElectoral\n\s+try:\n\s+padron = PadronElectoral\.objects\.get\(id=padron_id\)\n\s+\n\s+# Verificar si el usuario ya votó\n\s+if hasattr\(padron, \'voto\'\) and padron\.voto:\n\s+messages\.error\(request, \'Usted ya ha emitido su voto para este proceso electoral\'\)\n\s+return redirect\(\'administracion:index\'\)\n\s+\n\s+except PadronElectoral\.DoesNotExist:)'

# Texto de reemplazo
replacement = '''# Obtener la información del padrón
    from Aplicaciones.padron.models import PadronElectoral
    try:
        padron = PadronElectoral.objects.get(id=padron_id)
        
        # Verificar si ya existe un voto para este proceso y votante
        if Voto.objects.filter(proceso_electoral_id=proceso_id, votante=padron).exists():
            messages.error(request, 'Usted ya ha emitido su voto para este proceso electoral')
            return redirect('administracion:index')
            
        # Verificar si el usuario ya votó (compatibilidad con el campo voto en PadronElectoral)
        if hasattr(padron, 'voto') and padron.voto:
            messages.error(request, 'Usted ya ha emitido su voto para este proceso electoral')
            return redirect('administracion:index')
            
    except PadronElectoral.DoesNotExist:'''

# Realizar el reemplazo
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Escribir el contenido actualizado de vuelta al archivo
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(new_content)

print("El archivo ha sido actualizado correctamente.")
