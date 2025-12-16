from pathlib import Path
import os
import dj_database_url

# Directorio Base
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- SEGURIDAD ---
# En producción, usa la clave de Render. En local, usa una por defecto.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-clave-secreta-para-desarrollo-paso')

# DEBUG: Falso en Render (Producción), Verdadero en tu PC
DEBUG = 'RENDER' not in os.environ

# HOSTS PERMITIDOS
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
# También permitimos localhost para cuando trabajes en tu PC
ALLOWED_HOSTS.append('localhost')
ALLOWED_HOSTS.append('127.0.0.1')
ALLOWED_HOSTS.append('0.0.0.0')


# APLICACIONES INSTALADAS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # MIS APPS
    'apps.users',
    'apps.businesses',
]

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <--- VITAL: Estilos en la nube
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# PLANTILLAS (HTML)
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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- BASE DE DATOS ROBUSTA ---
# Lógica: Intenta leer la de Render. Si no existe, usa la local.
DB_RENDER = os.environ.get('DATABASE_URL')
DB_LOCAL = 'postgresql://paso_user:paso_password@db:5432/paso_beauty_db'

DATABASES = {
    'default': dj_database_url.config(
        default=DB_RENDER or DB_LOCAL,
        conn_max_age=600,
        ssl_require='RENDER' in os.environ # Solo exige SSL en la nube
    )
}

# VALIDACIÓN DE CONTRASEÑAS
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# IDIOMA Y ZONA HORARIA
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# --- ARCHIVOS ESTÁTICOS (CSS/Imágenes) ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Almacenamiento eficiente con compresión para Render
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CONFIGURACIÓN DE USUARIO
AUTH_USER_MODEL = 'users.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# VARIABLES DE ENTORNO (Integraciones)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
BOLD_SECRET_KEY = os.environ.get('BOLD_SECRET_KEY', '')

# REDIRECCIÓN DE AUTENTICACIÓN
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'