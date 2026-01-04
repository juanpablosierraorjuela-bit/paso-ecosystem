from django.contrib import admin
from .models import PlatformSettings

@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'whatsapp_number', 'instagram_link')
    
    # Esto impide crear más de una configuración (Singleton)
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
