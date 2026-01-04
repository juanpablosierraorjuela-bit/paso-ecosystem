import os
import sys

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_APP_DIR = os.path.join(BASE_DIR, "apps", "core_saas")

# Asegurar que la carpeta existe
if not os.path.exists(CORE_APP_DIR):
    os.makedirs(CORE_APP_DIR)

# --- 1. ARREGLAR MODELS.PY (EL CORAZÓN: USUARIO + FOOTER) ---
MODELS_PATH = os.path.join(CORE_APP_DIR, "models.py")
CONTENT_MODELS = """from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. MODELO DE USUARIO (CRÍTICO: Sin esto la página no arranca)
class User(AbstractUser):
    # Hereda toda la funcionalidad de Django (username, password, email)
    pass

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

# 2. MODELO DE CONFIGURACIÓN (FOOTER Y REDES)
class PlatformSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Paso Ecosystem")
    whatsapp_number = models.CharField(max_length=20, help_text="Ej: 573001234567", blank=True, null=True)
    instagram_link = models.CharField(max_length=200, help_text="URL completa de Instagram", blank=True, null=True)
    footer_text = models.CharField(max_length=200, default="Todos los derechos reservados", blank=True)

    def __str__(self):
        return "Configuración del Sistema"

    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuración del Sistema"
"""

# --- 2. ARREGLAR ADMIN.PY (PARA PODER EDITARLOS) ---
ADMIN_PATH = os.path.join(CORE_APP_DIR, "admin.py")
CONTENT_ADMIN = """from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import PlatformSettings, User

# Registramos el Usuario
admin.site.register(User, UserAdmin)

# Registramos la Configuración (Singleton: Solo permite crear uno)
@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'whatsapp_number', 'instagram_link')
    
    def has_add_permission(self, request):
        # Si ya existe una configuración, no deja crear otra
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
"""

# --- 3. ARREGLAR CONTEXT_PROCESSORS.PY (EL CEREBRO DEL FOOTER - BLINDADO) ---
CONTEXT_PATH = os.path.join(CORE_APP_DIR, "context_processors.py")
CONTENT_CONTEXT = """from .models import PlatformSettings
from django.db.utils import OperationalError, ProgrammingError

def global_settings(request):
    settings = None
    try:
        # Intenta obtener la configuración
        settings = PlatformSettings.objects.first()
    except (OperationalError, ProgrammingError):
        # Si la tabla no existe (error de migración), devuelve None y NO ROMPE la página
        settings = None
    except Exception:
        # Cualquier otro error, se ignora por seguridad
        settings = None
        
    return {'global_settings': settings}
"""

def ejecutar_rescate():
    print("🚑 INICIANDO MISIÓN DE RESCATE...")

    print("   1. Reescribiendo models.py (Restaurando User)...")
    with open(MODELS_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENT_MODELS)

    print("   2. Reescribiendo admin.py...")
    with open(ADMIN_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENT_ADMIN)

    print("   3. Reescribiendo context_processors.py (Modo Seguro)...")
    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENT_CONTEXT)

    print("✅ Archivos restaurados. Ahora DEBES ejecutar las migraciones.")

if __name__ == "__main__":
    ejecutar_rescate()