from pathlib import Path
import os
import environ # type: ignore

# Inicializar variables de entorno
env = environ.Env()
environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

# SEGURIDAD: En producción esto se toma de las variables de entorno de Render
SECRET_KEY = env('SECRET_KEY', default='django-insecure-clave-secreta-temporal-desarrollo')
DEBUG = env.bool('DEBUG', default=True) # En Render lo pondremos en False

ALLOWED_HOSTS = ['*'] # Ajustaremos esto al desplegar

# APLICACIONES DEL SISTEMA
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# TUS APLICACIONES (El Ecosistema PASO)
LOCAL_APPS = [
    'apps.core',        # Usuarios, Landing, Telegram
    'apps.businesses',  # Negocios, Servicios, Horarios
    'apps.marketplace', # Buscador, Geo, Clientes
    'apps.booking',     # Citas, Pagos
]

# LIBRERÍAS DE TERCEROS
THIRD_PARTY_APPS = [
    'corsheaders',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Motor de estáticos para Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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
        'DIRS': [BASE_DIR / 'templates'], # Carpeta global de templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.global_settings', # Footer Dinámico
                # AQUÍ PONDREMOS TU CONTEXT PROCESSOR DEL FOOTER MÁS ADELANTE
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# BASE DE DATOS
# Por defecto SQLite para desarrollo rápido hoy. En Render usaremos PostgreSQL.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Configuración automática para Render (si existe la variable DATABASE_URL)
import dj_database_url
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

# MODELO DE USUARIO PERSONALIZADO (CRUCIAL PARA TU LÓGICA)
AUTH_USER_MODEL = 'core.User' 

# VALIDACIÓN DE PASSWORD
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNACIONALIZACIÓN (Colombia)
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ARCHIVOS ESTÁTICOS Y MEDIA
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = 'dashboard'  # Redirige al Dispatcher
LOGOUT_REDIRECT_URL = 'home'
