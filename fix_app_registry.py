import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_APP_DIR = os.path.join(BASE_DIR, "apps", "core_saas")
APPS_FILE = os.path.join(CORE_APP_DIR, "apps.py")
INIT_FILE = os.path.join(CORE_APP_DIR, "__init__.py")

# --- 1. APPS.PY CORREGIDO (CON LABEL) ---
# Agregamos label='core_saas' para que coincida con AUTH_USER_MODEL
CONTENT_APPS = """from django.apps import AppConfig

class CoreSaasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core_saas'
    label = 'core_saas'  # <--- ¡ESTO FALTABA! Es la clave para que Django encuentre el User.
"""

# --- 2. __INIT__.PY CORREGIDO ---
# Aseguramos que Django cargue esta configuración por defecto
CONTENT_INIT = """default_app_config = 'apps.core_saas.apps.CoreSaasConfig'
"""

def aplicar_correccion_registro():
    print("🔧 Corrigiendo registro de la aplicación Core SaaS...")

    # 1. Reescribir apps.py
    with open(APPS_FILE, "w", encoding="utf-8") as f:
        f.write(CONTENT_APPS)
    print("   ✅ apps.py actualizado con label='core_saas'.")

    # 2. Reescribir __init__.py
    with open(INIT_FILE, "w", encoding="utf-8") as f:
        f.write(CONTENT_INIT)
    print("   ✅ __init__.py vinculado correctamente.")

    print("\n🚀 LISTO. Ahora sigue estos pasos obligatorios:")
    print("1. Ejecuta: python manage.py makemigrations core_saas")
    print("2. Ejecuta: python manage.py migrate")
    print("3. Sube los cambios a GitHub.")

if __name__ == "__main__":
    aplicar_correccion_registro()