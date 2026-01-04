import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_APP_DIR = os.path.join(BASE_DIR, "apps", "core_saas")
MODELS_PATH = os.path.join(CORE_APP_DIR, "models.py")
ADMIN_PATH = os.path.join(CORE_APP_DIR, "admin.py")

# --- 1. MODELS.PY (USUARIO + SETTINGS) ---
CONTENIDO_MODELS = """from django.db import models
from django.contrib.auth.models import AbstractUser

# --- 1. MODELO DE USUARIO (RESCATADO) ---
class User(AbstractUser):
    # Heredamos de AbstractUser para mantener username, email, password, etc.
    # Esto satisface la configuración AUTH_USER_MODEL = 'core_saas.User'
    pass

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

# --- 2. MODELO DE CONFIGURACIÓN (FOOTER) ---
class PlatformSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Paso Ecosystem")
    whatsapp_number = models.CharField(max_length=20, help_text="Ej: 573001234567", blank=True, null=True)
    instagram_link = models.CharField(max_length=200, help_text="URL completa de Instagram", blank=True, null=True)
    footer_text = models.CharField(max_length=200, default="Todos los derechos reservados", blank=True)

    def __str__(self):
        return "Configuración General de la Plataforma"

    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuración del Sistema"
"""

# --- 2. ADMIN.PY (REGISTRAR AMBOS) ---
CONTENIDO_ADMIN = """from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import PlatformSettings, User

# Registramos el Usuario para poder administrarlo
admin.site.register(User, UserAdmin)

# Registramos la configuración del footer
@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'whatsapp_number', 'instagram_link')
    
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
"""

def arreglar_modelos_usuario():
    print("🚑 Restaurando modelo User en core_saas...")
    
    with open(MODELS_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_MODELS)
        
    print("👮 Restaurando User en el panel de Admin...")
    with open(ADMIN_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_ADMIN)

    print("✅ ¡Arreglado! Ahora Django encontrará 'core_saas.User'.")

if __name__ == "__main__":
    arreglar_modelos_usuario()