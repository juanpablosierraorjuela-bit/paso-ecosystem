import os
import textwrap
import subprocess

def create_file(path, content):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(textwrap.dedent(content).strip())
    print(f"✅ Configuración Blindada: {path}")

print("🚑 ARREGLANDO BUCLE DE REDIRECCIONES (ERR_TOO_MANY_REDIRECTS)...")

# ==============================================================================
# 1. REESCRIBIR SETTINGS.PY CON LA CONFIGURACIÓN CORRECTA PARA RENDER
# ==============================================================================
# Agregamos el bloque vital: SECURE_PROXY_SSL_HEADER
settings_content = """
from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-genesis-key-2026')

# Detectamos si estamos en Render
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    DEBUG = False
else:
    DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Librerías
    'django.contrib.humanize',
    'rest_framework',
    'corsheaders',
    
    # Tus Apps
    'apps.core_saas',
    'apps.businesses',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'paso_ecosystem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.businesses.context_processors.owner_check',
            ],
        },
    },
]

WSGI_APPLICATION = 'paso_ecosystem.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# --- CONFIGURACIÓN DE SEGURIDAD VITAL PARA RENDER ---
if not DEBUG:
    # Esto soluciona el error de redirecciones infinitas
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Evita error CSRF al enviar formularios
    CSRF_TRUSTED_ORIGINS = ['https://' + RENDER_EXTERNAL_HOSTNAME] if RENDER_EXTERNAL_HOSTNAME else []

AUTH_PASSWORD_VALIDATORS = [] 

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

AUTH_USER_MODEL = 'core_saas.User'
LOGIN_URL = 'saas_login'
LOGIN_REDIRECT_URL = 'owner_dashboard' # Por defecto vamos al panel del dueño
LOGOUT_REDIRECT_URL = 'home'
"""

create_file('paso_ecosystem/settings.py', settings_content)

# ==============================================================================
# 2. SUBIDA AUTOMÁTICA
# ==============================================================================
print("🤖 Subiendo el parche de seguridad...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix: Add SECURE_PROXY_SSL_HEADER to solve redirect loop on Render"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("🚀 ¡ENVIADO! Espera el deploy y prueba iniciar sesión de nuevo.")
except Exception as e:
    print(f"⚠️ Error git: {e}")

print("💥 Limpiando...")
try:
    os.remove(__file__)
except: pass