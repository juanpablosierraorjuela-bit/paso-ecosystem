from django.db.models.signals import post_save
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
            f"🚀 *NUEVO DUEÑO REGISTRADO*\n\n"
            f"👤 *Usuario:* {instance.username}\n"
            f"📞 *Teléfono:* {instance.phone or 'Sin dato'}\n"
            f"🏙️ *Ciudad:* {instance.city or 'Sin dato'}\n\n"
            f"⚠️ *Estado:* Pendiente de Pago ($50k)\n"
            f"⏳ *Límite:* {deadline_str}\n"
            f"_El sistema eliminará esta cuenta si no se verifica el pago._"
        )
        send_telegram_message(msg)
