from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-clave-de-desarrollo-rapida'

DEBUG = True

ALLOWED_HOSTS = ['*']

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

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

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


# --- BLINDAJE DE DESPLIEGUE ---
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- SEGURIDAD RENDER ---
CSRF_TRUSTED_ORIGINS = ['https://paso-backend.onrender.com']

# SEGURIDAD PROD
SECURE_SSL_REDIRECT = os.environ.get('RENDER', False)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
