from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, GlobalSettings
import requests

# --- ACCIONES PERSONALIZADAS ---
@admin.action(description='✅ Verificar Pago (Activar Cuenta)')
def verify_payment(modeladmin, request, queryset):
    updated = queryset.update(is_verified_payment=True)
    modeladmin.message_user(request, f"{updated} dueños han sido marcados como PAGADOS.")

@admin.action(description='🚫 Revocar Pago (Desactivar)')
def revoke_payment(modeladmin, request, queryset):
    updated = queryset.update(is_verified_payment=False)
    modeladmin.message_user(request, f"{updated} dueños han sido marcados como PENDIENTES.")

# --- ADMIN DE USUARIOS ---
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'role', 'get_payment_status', 'city', 'date_joined')
    list_filter = ('role', 'is_verified_payment', 'city')
    actions = [verify_payment, revoke_payment]
    
    fieldsets = UserAdmin.fieldsets + (
        ('Datos PASO', {'fields': ('role', 'phone', 'city', 'is_verified_payment', 'workplace')}),
    )

    # SEMÁFORO DE PAGOS
    def get_payment_status(self, obj):
        if obj.role == 'OWNER':
            if obj.is_verified_payment:
                return format_html('<span style="color:white; background:green; padding:3px 8px; border-radius:10px; font-weight:bold;">ACTIVO ($50k)</span>')
            else:
                return format_html('<span style="color:white; background:red; padding:3px 8px; border-radius:10px; font-weight:bold;">PENDIENTE</span>')
        return "-"
    get_payment_status.short_description = 'Estado de Suscripción'

# --- ADMIN DE CONFIGURACIÓN GLOBAL ---
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'whatsapp_support', 'telegram_status')
    
    def telegram_status(self, obj):
        if obj.telegram_token and obj.telegram_chat_id:
            return format_html('<span style="color:green;">✅ Conectado</span>')
        return format_html('<span style="color:gray;">⚪ Sin Configurar</span>')
    telegram_status.short_description = "Bot Telegram"

    # Botón para probar Telegram (Acción dummy para el ejemplo)
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Aquí se podría disparar un mensaje de prueba
        
admin.site.register(User, CustomUserAdmin)
admin.site.register(GlobalSettings, GlobalSettingsAdmin)