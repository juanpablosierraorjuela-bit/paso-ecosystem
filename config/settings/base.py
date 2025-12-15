from pathlib import Path
import os
import dj_database_url
import sys

# ==========================================
# 1. CONFIGURACIÓN BASE Y DIRECTORIOS
# ==========================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Estamos en config/settings/base.py, así que subimos 3 niveles para llegar a la raíz.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ==========================================
# 2. SEGURIDAD Y ENTORNO
# ==========================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-clave-temporal-desarrollo-paso-beauty')

# SECURITY WARNING: don't run with debug turned on in production!
# Si la variable RENDER existe, DEBUG se apaga automáticamente.
DEBUG = 'RENDER' not in os.environ

# ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# --- CORRECCIONES CRÍTICAS PARA RENDER ---

# 1. Confiar en los orígenes de Render (Wildcard para cualquier subdominio)
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
]

# 2. Decirle a Django que confíe en el encabezado HTTPS del proxy de Render
# VITAL: Sin esto, Django cree que la conexión es insegura y bloquea formularios (Error 403).
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# 3. Configuraciones de cookies en Producción
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

# ==========================================
# 3. APLICACIONES INSTALADAS
# ==========================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Mis Aplicaciones
    'apps.users',
    'apps.businesses',
]

# ==========================================
# 4. MIDDLEWARE
# ==========================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <--- VITAL: Manejo de estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ==========================================
# 5. PLANTILLAS (TEMPLATES)
# ==========================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Busca en la carpeta templates en la raíz
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ==========================================
# 6. BASE DE DATOS
# ==========================================

# Usa la base de datos de Render si está disponible, si no, usa SQLite local.
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        ssl_require=not DEBUG  # Requiere SSL en producción
    )
}

# ==========================================
# 7. VALIDACIÓN DE PASSWORD & USUARIO
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'users.User'

# ==========================================
# 8. IDIOMA Y ZONA HORARIA
# ==========================================

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ==========================================
# 9. ARCHIVOS ESTÁTICOS (SOLUCIÓN PANTALLA BLANCA)
# ==========================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuración WhiteNoise
if not DEBUG:
    # Usamos CompressedStaticFilesStorage en lugar de Manifest...
    # Esto evita que la página se rompa si falta algún archivo referenciado.
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==========================================
# 10. OTRAS CONFIGURACIONES
# ==========================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# Variables de entorno opcionales
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
BOLD_SECRET_KEY = os.environ.get('BOLD_SECRET_KEY')