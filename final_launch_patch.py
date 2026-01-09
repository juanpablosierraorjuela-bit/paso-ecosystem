import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. ACTUALIZAR REQUIREMENTS.TXT (Cloudinary + DB)
# ==========================================
def update_requirements():
    print("📦 INSTALANDO LIBRERÍAS DE PRODUCCIÓN (Cloudinary + Postgres)...")
    req_path = BASE_DIR / 'requirements.txt'
    
    new_packages = [
        'dj-database-url>=2.1.0',
        'psycopg2-binary>=2.9.9',
        'cloudinary>=1.36.0',
        'django-cloudinary-storage>=0.3.0',
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
    print("✅ requirements.txt actualizado.")

# ==========================================
# 2. REESCRIBIR SETTINGS.PY (MODO DIOS)
# ==========================================
settings_content = """
import os
from pathlib import Path
import dj_database_url

# --- RUTA BASE ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SEGURIDAD CRÍTICA ---
# Si no hay SECRET_KEY en Render, usa una insegura (SOLO PARA LOCAL)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-clave-temporal-cambiar-en-prod')

# DEBUG: True solo si NO estamos en Render
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = ['*'] # Render maneja el dominio, esto es seguro aquí.

# --- APLICACIONES ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # CLOUDINARY (MEDIOS) Y WHITENOISE (ESTÁTICOS)
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'cloudinary_storage', # Para guardar fotos en la nube
    'cloudinary',
    
    # MIS APPS
    'apps.core',
    'apps.businesses',
    'apps.marketplace',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Vital para estilos
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

# --- BASE DE DATOS (POSTGRESQL OBLIGATORIO EN PROD) ---
# En local usa SQLite, en Render usa la URL de Postgres
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# --- VALIDACIÓN DE CONTRASEÑAS ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- INTERNACIONALIZACIÓN ---
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# --- ARCHIVOS ESTÁTICOS (CSS/JS - WHITENOISE) ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- ARCHIVOS MULTIMEDIA (FOTOS - CLOUDINARY) ---
# Esto evita que se borren las fotos al reiniciar el servidor
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}

if 'RENDER' in os.environ:
    # En Producción usamos Cloudinary
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = '/media/'
else:
    # En Local usamos carpetas normales
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# --- MODELO DE USUARIO ---
AUTH_USER_MODEL = 'core.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dispatch'
LOGOUT_REDIRECT_URL = 'home'

# --- CONFIGURACIÓN DE CORREO (SMTP cPanel) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'mail.pasotunja.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 465))
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f"Soporte PASO <{os.environ.get('EMAIL_HOST_USER')}>"

# --- SEGURIDAD DE PRODUCCIÓN (EL BÚNKER) ---
if 'RENDER' in os.environ:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
"""

def apply_final_patch():
    print("🛡️ APLICANDO PARCHE DE INFRAESTRUCTURA FINAL...")
    
    # 1. Update Requirements
    update_requirements()
    
    # 2. Overwrite Settings
    settings_path = BASE_DIR / 'config' / 'settings.py'
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(settings_content.strip())
    print("✅ settings.py reescrito para producción (DB + Cloudinary + Seguridad).")

if __name__ == "__main__":
    apply_final_patch()