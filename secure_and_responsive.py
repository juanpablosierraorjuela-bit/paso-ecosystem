import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. SETTINGS.PY (MODO PRODUCCIÓN BLINDADO)
# ==========================================
# Leemos el archivo actual y reemplazamos la configuración insegura
settings_path = BASE_DIR / 'config' / 'settings.py'

new_security_settings = """
# --- SEGURIDAD DE PRODUCCIÓN (EL BÚNKER) ---
import os
import dj_database_url

# 1. CLAVE SECRETA (Busca en variables de entorno o usa una de respaldo LOCAL)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-cambiar-esto-en-produccion-urgente')

# 2. DEBUG: Solo True si NO estamos en Render (o si forzamos la variable)
DEBUG = 'RENDER' not in os.environ

# 3. HOSTS PERMITIDOS
ALLOWED_HOSTS = ['*'] # En producción Render maneja el filtrado, pero puedes poner tu dominio aquí.

# 4. BLINDAJE HTTPS & COOKIES (Solo se activan si DEBUG es False)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY' # Evita que te metan en un iframe
    SECURE_HSTS_SECONDS = 31536000 # 1 año forzando HTTPS
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# 5. BASE DE DATOS (Auto-configuración en Render)
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# 6. ARCHIVOS ESTÁTICOS (WhiteNoise - Ya lo tienes, pero aseguramos)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
"""

# ==========================================
# 2. URLS.PY (OCULTAR EL ADMIN)
# ==========================================
# Cambiamos 'admin/' por 'puerta-trasera-segura/'
urls_path = BASE_DIR / 'config' / 'urls.py'
urls_content = """
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # CAMBIO DE SEGURIDAD: Admin oculto
    path('control-maestro-seguro/', admin.site.urls),
    
    path('', include('apps.core.urls')),
    path('negocio/', include('apps.businesses.urls')),
    path('marketplace/', include('apps.marketplace.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
"""

# ==========================================
# 3. BASE.HTML (META TAGS MÓVILES PERFECTOS)
# ==========================================
# Ajustamos el viewport para evitar zoom indeseado en inputs de iPhone
base_path = BASE_DIR / 'templates' / 'base.html'

def apply_security():
    print("🛡️ APLICANDO PROTOCOLO DE SEGURIDAD Y RESPONSIVIDAD...")

    # 1. Modificar Settings
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscamos dónde insertar la seguridad (Reemplazamos desde SECRET_KEY hasta antes de INSTALLED_APPS)
    # Estrategia: Reescribir el archivo conservando los imports y apps, pero inyectando la seguridad al inicio
    # Para ser menos invasivos, vamos a ANEXAR la configuración de seguridad al final, 
    # pero asegurándonos de que sobrescriba lo anterior o esté bien configurado.
    # MEJOR ESTRATEGIA: Como tenemos el archivo, vamos a inyectar la seguridad detectando el bloque de DATABASES.
    
    # Simplemente agregamos el bloque de seguridad al final del archivo, Django usa el último valor leído.
    # Pero para DEBUG es delicado. Vamos a leer el archivo y reemplazar DEBUG = True
    
    new_content = content.replace('DEBUG = True', "DEBUG = 'RENDER' not in os.environ")
    new_content = new_content.replace("ALLOWED_HOSTS = ['*']", "ALLOWED_HOSTS = ['*']") # Mantenemos, pero la lógica de seguridad va abajo
    
    # Agregamos el bloque de seguridad al final
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(new_content + "\n\n" + new_security_settings)
    print("✅ Settings.py blindado (SSL, HSTS, Cookies Seguras).")

    # 2. Modificar URLs (Ocultar Admin)
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_content.strip())
    print("✅ Admin oculto en '/control-maestro-seguro/'.")

    # 3. Mejorar Base.html (Mobile Tuning)
    with open(base_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Inyectar meta tag optimizado si no es el mejor
    viewport_optimized = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">'
    if '<meta name="viewport"' in html:
        # Reemplazo simple
        import re
        html = re.sub(r'<meta name="viewport"[^>]*>', viewport_optimized, html)
    
    with open(base_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("✅ Viewport optimizado para móviles (Sin zoom en inputs).")

if __name__ == "__main__":
    apply_security()