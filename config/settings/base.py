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
# 2. SEGURIDAD Y ENTORNO (CRÍTICO)
# ==========================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-clave-temporal-desarrollo-paso-beauty')

# SECURITY WARNING: don't run with debug turned on in production!
# Si la variable RENDER existe, DEBUG se apaga automáticamente.
DEBUG = 'RENDER' not in os.environ

# ALLOWED_HOSTS
# En Render, permitimos el host externo y también localhost para pruebas.
# Usamos '*' temporalmente para asegurar que no bloquee por nombre de dominio, 
# pero idealmente debería ser la lista de dominios permitidos.
ALLOWED_HOSTS = ['*']

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# --- CORRECCIÓN DEFINITIVA ERROR 403 CSRF EN RENDER ---

# 1. Confiar en los orígenes de Render (Wildcard para cualquier subdominio)
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
]

# 2. Si tienes un dominio personalizado, agrégalo aquí también:
# CSRF_TRUSTED_ORIGINS.append('https://mi-dominio.com')

# 3. Decirle a Django que confíe en el encabezado HTTPS del proxy de Render
# Sin esto, Django cree que la petición es insegura y bloquea el CSRF.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# 4. Configuraciones adicionales de cookies en Producción
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    # HSTS (Opcional, descomentar si ya tienes HTTPS estable)
    # SECURE_HSTS_SECONDS = 31536000
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True

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
    
    # Librerías de terceros
    # 'corsheaders', # Descomentar si usas React/Vue externo en el futuro

    # Mis Aplicaciones (Apps Locales)
    'apps.users',
    'apps.businesses',
]

# ==========================================
# 4. MIDDLEWARE
# ==========================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <--- VITAL: Justo después de SecurityMiddleware
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

# Configuración robusta: Intenta usar la variable de entorno, si no, usa SQLite local.
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        ssl_require=not DEBUG  # Requiere SSL en producción (Render Postgres)
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

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'users.User'

# ==========================================
# 8. IDIOMA Y ZONA HORARIA
# ==========================================

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ==========================================
# 9. ARCHIVOS ESTÁTICOS (CSS, JS, IMAGES)
# ==========================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Motor de almacenamiento para producción (WhiteNoise)
# Esto comprime y cachea los archivos estáticos automáticamente.
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Configuración de Media (Archivos subidos por el usuario)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==========================================
# 10. OTRAS CONFIGURACIONES
# ==========================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirecciones tras Login/Logout
LOGIN_REDIRECT_URL = 'dashboard'  # Asegúrate que esta URL name exista en urls.py
LOGOUT_REDIRECT_URL = 'home'      # Asegúrate que esta URL name exista en urls.py
LOGIN_URL = 'login'

# Variables de entorno personalizadas (Opcional)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
BOLD_SECRET_KEY = os.environ.get('BOLD_SECRET_KEY')