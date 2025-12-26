import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / 'config' / 'settings.py'

def arreglar_seguridad():
    print(f"🛡️ Arreglando seguridad en: {SETTINGS_PATH}")
    
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. SOLUCIÓN ERROR 403 (CSRF)
    # Agregamos el dominio de Render a los orígenes de confianza
    if "CSRF_TRUSTED_ORIGINS" not in content:
        csrf_fix = "\n# --- SEGURIDAD RENDER ---\nCSRF_TRUSTED_ORIGINS = ['https://paso-backend.onrender.com']\n"
        content += csrf_fix
        print("   ✅ Dominio agregado a CSRF_TRUSTED_ORIGINS.")
    else:
        print("   ℹ️ Ya existía configuración CSRF (Verifica que el dominio esté correcto).")

    # 2. ASEGURAR BASE DE DATOS (Por si acaso se borró)
    # Reemplazamos la conexión que falla ('HOST': 'db') por la correcta
    old_db_pattern = "'HOST': 'db'"
    if old_db_pattern in content:
        import re
        # Bloque nuevo que usa la URL de Render automáticamente
        new_db_block = """# --- BASE DE DATOS HÍBRIDA ---
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600
    )
}"""
        # Buscamos y reemplazamos todo el bloque DATABASES viejo
        content = re.sub(r"DATABASES\s*=\s*\{[^}]+\{[^}]+\}[^}]+\}", new_db_block, content, flags=re.DOTALL)
        
        # Aseguramos que el import no se duplique
        if "import dj_database_url" not in content:
            content = "import dj_database_url\n" + content
            
        print("   ✅ Base de datos corregida (dj_database_url restaurado).")

    # Guardamos el archivo
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    arreglar_seguridad()