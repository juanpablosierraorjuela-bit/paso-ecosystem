import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_APP_DIR = os.path.join(BASE_DIR, "apps", "core_saas")
CONTEXT_PATH = os.path.join(CORE_APP_DIR, "context_processors.py")

# --- CONTEXT PROCESSOR BLINDADO (SAFE MODE) ---
# Usamos un try/except para que si la base de datos falla, la página siga viva.
CONTENIDO_CONTEXT = """from .models import PlatformSettings
from django.db.utils import OperationalError, ProgrammingError

def global_settings(request):
    settings = None
    try:
        # Intentamos buscar la configuración
        settings = PlatformSettings.objects.first()
    except (OperationalError, ProgrammingError):
        # Si la tabla no existe (porque faltan migraciones), no hacemos nada
        # Esto evita el Error 500
        settings = None
    except Exception as e:
        # Cualquier otro error, lo ignoramos para mantener el sitio arriba
        settings = None
        
    return {'global_settings': settings}
"""

def aplicar_parche_seguridad():
    print("🛡️ Aplicando parche de seguridad al Context Processor...")
    
    # Asegurar que el directorio existe
    if not os.path.exists(CORE_APP_DIR):
        print("❌ No encuentro la carpeta apps/core_saas. Verifica tu estructura.")
        return

    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_CONTEXT)

    print("✅ Parche aplicado. Ahora el sitio no se caerá si falta la tabla.")

if __name__ == "__main__":
    aplicar_parche_seguridad()