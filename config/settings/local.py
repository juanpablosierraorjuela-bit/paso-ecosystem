from .base import *

# ACTIVAR MODO DESARROLLO
DEBUG = True

# Permitir conexiones locales
ALLOWED_HOSTS = ["*"]

# --- ARREGLO PARA WINDOWS ---
# Usamos SQLite en lugar de intentar conectar a "db"
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}