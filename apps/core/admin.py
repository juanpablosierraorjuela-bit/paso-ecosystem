from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import User, PlatformSettings
from .utils import send_telegram_message

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role_badge', 'is_verified_payment', 'date_joined')
    list_filter = ('role', 'is_verified_payment', 'city')
    search_fields = ('username', 'email', 'phone')
    
    def role_badge(self, obj):
        colors = {
            'ADMIN': 'black',
            'OWNER': 'purple',
            'EMPLOYEE': 'blue',
            'CLIENT': 'green',
        }
        color = colors.get(obj.role, 'grey')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 15px;">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = 'Rol'

@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'telegram_status', 'support_whatsapp')
    
    def telegram_status(self, obj):
        if obj.telegram_bot_token and obj.telegram_chat_id:
            return " Conectado"
        return " Sin Configurar"
    
    change_list_template = "admin/settings_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('test-telegram/', self.test_telegram_connection, name='test_telegram'),
        ]
        return custom_urls + urls

    def test_telegram_connection(self, request):
        success = send_telegram_message(" *PRUEBA DE CONEXIÓN PASO*\n\nSi lees esto, el sistema está en línea y vigilando.")
        if success:
            self.message_user(request, " Mensaje enviado con éxito a Telegram.", messages.SUCCESS)
        else:
            self.message_user(request, " Error al enviar. Revisa el Token y el Chat ID.", messages.ERROR)
        return redirect('..')
