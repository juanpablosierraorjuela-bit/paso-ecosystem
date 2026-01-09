import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. ACTUALIZAR REQUIREMENTS.TXT (Solo lo esencial)
# ==========================================
def update_requirements():
    print("📦 INSTALANDO MOTORES DE PRODUCCIÓN...")
    req_path = BASE_DIR / 'requirements.txt'
    
    # Quitamos cloudinary de la lista, dejamos solo DB y Servidor
    new_packages = [
        'dj-database-url>=2.1.0',
        'psycopg2-binary>=2.9.9',
        'gunicorn>=21.2.0',
        'whitenoise>=6.6.0'
    ]
    
    current_content = ""
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            current_content = f.read()
            
    with open(req_path, 'a') as f:
        for package in new_packages:
            if package.split('>')[0] not in current_content:
                f.write(f'\n{package}')
    print("✅ requirements.txt listo para Render.")

# ==========================================
# 2. BLINDAR SETTINGS.PY (SIN IMÁGENES)
# ==========================================
settings_content = """
import os
from pathlib import Path
import dj_database_url

# --- RUTA BASE ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SEGURIDAD: LEER DE RENDER ---
# Usa la variable de entorno o una clave tonta si estamos en local
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-key-12345')

# DEBUG: Se apaga automáticamente en Render
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = ['*']

# --- APPS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Estáticos
    'django.contrib.staticfiles',
    
    # MIS APPS
    'apps.core',
    'apps.businesses',
    'apps.marketplace',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Vital para el diseño
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'apps.core.context_processors.global_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- BASE DE DATOS (POSTGRES EN NUBE / SQLITE EN LOCAL) ---
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# --- VALIDADORES DE CLAVE ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- IDIOMA Y HORA ---
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# --- ARCHIVOS ESTÁTICOS (DISEÑO) ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- ARCHIVOS MEDIA (FOTOS) - CONFIGURACIÓN EFÍMERA ---
# Como no usaremos Cloudinary, esto se guarda en el disco del servidor.
# ADVERTENCIA: En Render, estas fotos se borran cada vez que haces deploy.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- REDIRECCIONES ---
AUTH_USER_MODEL = 'core.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dispatch'
LOGOUT_REDIRECT_URL = 'home'

# --- EMAIL (Tu cPanel) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'mail.pasotunja.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 465))
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f"Soporte PASO <{os.environ.get('EMAIL_HOST_USER')}>"

# --- SEGURIDAD DE PRODUCCIÓN ---
if 'RENDER' in os.environ:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
"""

def apply_lite_patch():
    print("🛡️ APLICANDO CONFIGURACIÓN LIGERA (SOLO DB + SEGURIDAD)...")
    
    # 1. Update Requirements
    update_requirements()
    
    # 2. Overwrite Settings
    settings_path = BASE_DIR / 'config' / 'settings.py'
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(settings_content.strip())
    print("✅ settings.py blindado (Sin Cloudinary).")

if __name__ == "__main__":
    apply_lite_patch()