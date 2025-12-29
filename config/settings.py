from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --- SEGURIDAD CRÍTICA (CORREGIDO) ---
# En producción (Render), toma la clave del entorno. En local, usa la insegura por defecto.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-clave-de-desarrollo-rapida')

# En producción, DEBUG debe ser False. Se controla vía variable de entorno.
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Define los hosts permitidos separando por comas (ej: paso-backend.onrender.com,localhost)
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    
    # 'apps.users',      # <--- DESACTIVADO: Conflictúa con el nuevo sistema core_saas
    'apps.businesses',
    'core_saas',         # <--- NUEVO: Tu arquitectura nivel Dios
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <--- AUDITORÍA: NECESARIO PARA ESTÁTICOS EN RENDER
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
                'apps.businesses.context_processors.owner_check',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Configuración de Base de Datos (PostgreSQL)
# --- BASE DE DATOS (Híbrida: Render vs Local) ---
# En Render: Usa DATABASE_URL (PostgreSQL)
# En Local: Usa db.sqlite3 (SQLite)
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# --- STATIC FILES (Configuración Blindada para Producción) ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Compresión y cacheo eficiente para producción (WhiteNoise)
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CAMBIO CRÍTICO: NUEVO MODELO DE USUARIO ---
AUTH_USER_MODEL = 'core_saas.User'  # Apunta al nuevo sistema de Roles

# --- NUEVAS REDIRECCIONES DE LOGIN (SaaS) ---
LOGIN_URL = 'login'           # Si intentan entrar sin permiso, van al login
LOGIN_REDIRECT_URL = 'dashboard'  # Al entrar, el view decide a donde van
LOGOUT_REDIRECT_URL = 'home' # Al salir, vuelven al login

# --- FIX PARA FECHAS HTML5 ---
DATETIME_INPUT_FORMATS = [
    '%Y-%m-%dT%H:%M',
    '%Y-%m-%d %H:%M',
    '%Y-%m-%d %H:%M:%S',
]
# Permitir logout mediante enlace directo
LOGOUT_ON_GET = True

# --- SEGURIDAD RENDER Y PRODUCCIÓN ---
CSRF_TRUSTED_ORIGINS = ['https://paso-backend.onrender.com']

# Detectar si estamos en Render para activar seguridad extra
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

# Activar seguridad SSL y Cookies SOLO si no estamos en modo DEBUG (Producción)
if not DEBUG:
    SECURE_SSL_REDIRECT = False  # Render ya maneja el HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    # En desarrollo local (Debug=True), permitimos HTTP normal para no bloquearte
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False