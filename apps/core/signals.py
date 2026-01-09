from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, GlobalSettings
import requests

def send_telegram_message(message):
    try:
        settings = GlobalSettings.objects.first()
        if settings and settings.telegram_token and settings.telegram_chat_id:
            url = f"https://api.telegram.org/bot{settings.telegram_token}/sendMessage"
            data = {"chat_id": settings.telegram_chat_id, "text": message, "parse_mode": "Markdown"}
            requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(f"Error enviando Telegram: {e}")

@receiver(post_save, sender=User)
def notify_new_owner(sender, instance, created, **kwargs):
    if created and instance.role == 'OWNER':
        msg = (
            f"🚀 *NUEVO DUEÑO REGISTRADO*\n\n"
            f"👤 *Nombre:* {instance.first_name} {instance.last_name}\n"
            f"🏪 *Usuario:* {instance.username}\n"
            f"📍 *Ciudad:* {instance.city}\n\n"
            f"⚠️ *Estado:* Pendiente de Pago (24h restantes)"
        )
        send_telegram_message(msg)