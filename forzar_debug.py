import os

# Contenido corregido del archivo settings.py
# El cambio principal es: DEBUG = True (sin condiciones)
settings_content = """from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --- SEGURIDAD CRÍTICA ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-clave-de-desarrollo-rapida')

# --- ¡CAMBIO IMPORTANTE AQUÍ! ---
# Forzamos el modo DEBUG a True para que Docker te muestre los errores en pantalla.
DEBUG = True 

# Permitimos todo en local
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    
    # 'apps.users',      # DESACTIVADO: Conflictúa con el nuevo sistema
    'apps.businesses',
    'core_saas',         # NUEVO: Tu motor principal
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
                'apps.businesses.context_processors.owner_check',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Configuración de Base de Datos
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
STATIC_ROOT = BASE_DIR / 'staticfiles'

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- MODELO DE USUARIO ---
AUTH_USER_MODEL = 'core_saas.User'

# --- REDIRECCIONES ---
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
LOGOUT_ON_GET = True

DATETIME_INPUT_FORMATS = [
    '%Y-%m-%dT%H:%M',
    '%Y-%m-%d %H:%M',
    '%Y-%m-%d %H:%M:%S',
]

# --- SEGURIDAD ---
CSRF_TRUSTED_ORIGINS = ['https://paso-backend.onrender.com']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

# Desactivamos redirecciones SSL forzadas porque estamos en local (DEBUG=True)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
"""

def main():
    try:
        # Escribimos el archivo settings.py con la configuración forzada
        with open('config/settings.py', 'w', encoding='utf-8') as f:
            f.write(settings_content)
        print("✅ ¡Listo! settings.py arreglado con DEBUG = True.")
        print("👉 Ahora tu servidor se reiniciará solo. Recarga la página http://localhost:8000")
        print("⚠️ Deberías ver una pantalla amarilla con el error exacto en lugar del Error 500.")
    except Exception as e:
        print(f"❌ Error al escribir el archivo: {e}")

if __name__ == "__main__":
    main()