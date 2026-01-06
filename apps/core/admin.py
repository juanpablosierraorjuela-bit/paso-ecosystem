from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import User, PlatformSettings
from .utils import send_telegram_message

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'status_payment', 'is_active_account', 'date_joined')
    list_filter = ('role', 'is_verified_payment', 'is_active_account')
    actions = ['verify_payment_manually']

    def status_payment(self, obj):
        if obj.role != 'OWNER':
            return "-"
        if obj.is_verified_payment:
            return format_html('<span style="color:green;">✅ Verificado</span>')
        
        hours_passed = obj.hours_since_registration
        hours_left = 24 - hours_passed
        if hours_left > 0:
            return format_html(f'<span style="color:orange;">⏳ Restan {int(hours_left)}h</span>')
        else:
            return format_html('<span style="color:red;">💀 Vencido</span>')
    
    status_payment.short_description = "Estado Mensualidad"

    def verify_payment_manually(self, request, queryset):
        updated = queryset.update(is_verified_payment=True, is_active_account=True, is_active=True)
        self.message_user(request, f"{updated} usuarios marcados como pagados.", messages.SUCCESS)
    verify_payment_manually.short_description = "✅ Confirmar Pago de $50k"

@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'telegram_status')
    
    def telegram_status(self, obj):
        if obj.telegram_bot_token and obj.telegram_chat_id:
            return "🟢 Configurado"
        return "🔴 Sin configurar"

    def response_change(self, request, obj):
        if "_save" in request.POST:
            if obj.telegram_bot_token and obj.telegram_chat_id:
                success = send_telegram_message("🤖 *Prueba de Conexión PASO*\n¡Sistema operativo y conectado!")
                if success:
                    self.message_user(request, "✅ Conexión a Telegram exitosa.", messages.SUCCESS)
                else:
                    self.message_user(request, "❌ Error al conectar con Telegram.", messages.ERROR)
        return super().response_change(request, obj)
