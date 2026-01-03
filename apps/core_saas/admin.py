from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PlatformSettings

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('Información Extra Paso', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Extra Paso', {'fields': ('role', 'phone')}),
    )

@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ('whatsapp_number', 'instagram_link')
    # Impide crear más de un registro para evitar errores
    def has_add_permission(self, request):
        return not PlatformSettings.objects.exists()