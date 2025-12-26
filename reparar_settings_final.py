import os
from pathlib import Path

# Ruta al archivo settings.py
BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / 'config' / 'settings.py'

def arreglar_definitivo():
    print(f"🔧 Reparando: {SETTINGS_PATH}")
    
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # 1. Asegurar que tenemos el import de dj_database_url
    if "import dj_database_url" not in contenido:
        # Lo agregamos después de 'import os'
        contenido = contenido.replace("import os", "import os\nimport dj_database_url")
        print("   ✅ Import 'dj_database_url' agregado.")

    # 2. Reemplazar el bloque de DATABASES problemático
    # Este es el bloque exacto que tienes ahora y que causa el error
    bloque_malo = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'marketplace_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres_password',
        'HOST': 'db',
        'PORT': 5432,
    }
}"""

    bloque_bueno = """# --- BASE DE DATOS (Híbrida: Render vs Local) ---
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600
    )
}"""

    if bloque_malo in contenido:
        contenido = contenido.replace(bloque_malo, bloque_bueno)
        print("   ✅ Configuración de base de datos corregida (Adiós 'HOST: db').")
    else:
        # Si no coincide exacto por espacios, forzamos un reemplazo más agresivo
        import re
        patron = r"DATABASES\s*=\s*\{[^}]+\{[^}]+\}[^}]+\}"
        if re.search(patron, contenido, re.DOTALL):
            contenido = re.sub(patron, bloque_bueno, contenido, flags=re.DOTALL)
            print("   ✅ Configuración de base de datos corregida (Reemplazo forzado).")
        else:
            print("   ⚠️ No pude encontrar el bloque DATABASES automáticamente. Revisa el archivo.")

    # Guardar cambios
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.write(contenido)

if __name__ == "__main__":
    arreglar_definitivo()