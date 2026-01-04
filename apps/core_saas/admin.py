from django.contrib import admin
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
