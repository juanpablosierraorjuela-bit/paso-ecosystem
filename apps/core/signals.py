from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .utils import send_telegram_message

User = get_user_model()

@receiver(post_save, sender=User)
def notify_new_owner(sender, instance, created, **kwargs):
    """
    Detecta cuando se crea un nuevo DUEÑO y te avisa por Telegram.
    """
    if created and instance.role == User.Role.OWNER:
        msg = (
            f" *¡NUEVO UNICORNIO CAPTURADO!*\n\n"
            f" *Usuario:* {instance.first_name} {instance.last_name}\n"
            f" *Email:* {instance.email}\n"
            f" *Tel:* {instance.phone}\n"
            f" *Ciudad:* {instance.city}\n\n"
            f" *El contador de 24h ha iniciado.*"
        )
        send_telegram_message(msg)
