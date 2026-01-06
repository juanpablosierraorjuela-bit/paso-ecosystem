import os
import subprocess
import sys

# --- DEFINICIÓN DE CONTENIDOS ---

utils_content = """import requests
from .models import PlatformSettings

def send_telegram_message(message):
    try:
        config = PlatformSettings.objects.first()
        if not config or not config.telegram_bot_token or not config.telegram_chat_id:
            print("⚠️ Telegram no configurado en el Admin.")
            return False

        url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
        data = {
            "chat_id": config.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, data=data, timeout=5)
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error enviando Telegram: {e}")
        return False
"""

signals_content = """from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .utils import send_telegram_message
from datetime import timedelta

User = get_user_model()

@receiver(post_save, sender=User)
def notify_new_owner_registration(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.OWNER:
        deadline = instance.registration_timestamp + timedelta(hours=24)
        deadline_str = deadline.strftime("%d/%m %I:%M %p")

        msg = (
            f"🚀 *NUEVO DUEÑO REGISTRADO*\\n\\n"
            f"👤 *Usuario:* {instance.username}\\n"
            f"📞 *Teléfono:* {instance.phone or 'Sin dato'}\\n"
            f"🏙️ *Ciudad:* {instance.city or 'Sin dato'}\\n\\n"
            f"⚠️ *Estado:* Pendiente de Pago ($50k)\\n"
            f"⏳ *Límite:* {deadline_str}\\n"
            f"_El sistema eliminará esta cuenta si no se verifica el pago._"
        )
        send_telegram_message(msg)
"""

apps_content = """from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'

    def ready(self):
        import apps.core.signals
"""

reaper_content = """from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from apps.booking.models import Appointment
from apps.core.utils import send_telegram_message

User = get_user_model()

class Command(BaseCommand):
    help = 'El Segador: Elimina usuarios morosos y citas expiradas.'

    def handle(self, *args, **kwargs):
        self.stdout.write("💀 The Reaper se ha despertado...")
        now = timezone.now()
        
        # FASE 1: Morosos (24h)
        deadline_soft = now - timedelta(hours=24)
        morosos = User.objects.filter(
            role='OWNER', 
            is_verified_payment=False, 
            is_active_account=True,
            registration_timestamp__lte=deadline_soft
        )
        
        count_soft = 0
        for user in morosos:
            user.is_active_account = False
            user.is_active = False
            user.save()
            count_soft += 1
            send_telegram_message(f"🗑️ *Cuenta Desactivada (24h)*\\nUsuario: {user.username}")

        # FASE 2: Eliminación Definitiva (72h)
        deadline_hard = now - timedelta(hours=72)
        basura = User.objects.filter(
            role='OWNER',
            is_active_account=False,
            registration_timestamp__lte=deadline_hard
        )
        count_hard = basura.count()
        basura.delete()

        # FASE 3: Citas Pendientes (60 min)
        expiration_time = now - timedelta(minutes=60)
        expired_appointments = Appointment.objects.filter(
            status='PENDING',
            created_at__lte=expiration_time
        )
        count_apps = expired_appointments.count()
        expired_appointments.delete()

        self.stdout.write(self.style.SUCCESS(
            f"✅ Ejecución Finalizada:\\n"
            f"- Morosos desactivados: {count_soft}\\n"
            f"- Morosos eliminados: {count_hard}\\n"
            f"- Citas liberadas: {count_apps}"
        ))
"""

admin_content = """from django.contrib import admin
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
                success = send_telegram_message("🤖 *Prueba de Conexión PASO*\\n¡Sistema operativo y conectado!")
                if success:
                    self.message_user(request, "✅ Conexión a Telegram exitosa.", messages.SUCCESS)
                else:
                    self.message_user(request, "❌ Error al conectar con Telegram.", messages.ERROR)
        return super().response_change(request, obj)
"""

# --- FUNCIONES DE UTILIDAD ---

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Archivo creado/actualizado: {path}")

def update_requirements():
    req_path = 'requirements.txt'
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            if 'requests' not in f.read():
                with open(req_path, 'a') as f_append:
                    f_append.write('\nrequests\n')
                print("✅ 'requests' agregado a requirements.txt")
    else:
        write_file(req_path, "requests\n")

def run_git_commands():
    try:
        print("🐙 Ejecutando Git...")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "feat: Implement Superuser Automation (Telegram + Reaper)"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 ¡Código subido a GitHub exitosamente!")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error en Git (tal vez no hay cambios o no estás logueado): {e}")

# --- EJECUCIÓN PRINCIPAL ---

if __name__ == "__main__":
    print("🛠️  Iniciando inyección de lógica Superusuario...")
    
    # 1. Crear archivos de lógica
    write_file('apps/core/utils.py', utils_content)
    write_file('apps/core/signals.py', signals_content)
    write_file('apps/core/apps.py', apps_content)
    write_file('apps/core/admin.py', admin_content)
    
    # 2. Crear comando 'The Reaper' y estructura de carpetas
    write_file('apps/core/management/__init__.py', "")
    write_file('apps/core/management/commands/__init__.py', "")
    write_file('apps/core/management/commands/run_reaper.py', reaper_content)
    
    # 3. Actualizar dependencias
    update_requirements()
    
    # 4. Git Push
    run_git_commands()
    
    # 5. Autodestrucción
    try:
        os.remove(__file__)
        print("💥 Script autodestruido. ¡Misión cumplida!")
    except Exception as e:
        print(f"No se pudo autodestruir: {e}")