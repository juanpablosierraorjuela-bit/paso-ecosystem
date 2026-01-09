from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-genesis-key-change-me-in-production'
DEBUG = 'RENDER' not in os.environ
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # APPS DEL ECOSISTEMA PASO
    'apps.core',
    'apps.businesses',
    'apps.marketplace',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
                # Context Processor para el Footer Dinámico
                'apps.core.context_processors.global_settings', 
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- MODELO DE USUARIO PERSONALIZADO ---
AUTH_USER_MODEL = 'core.User'

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# --- REDIRECCIÓN INTELIGENTE ---
LOGIN_REDIRECT_URL = 'dispatch'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'



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
