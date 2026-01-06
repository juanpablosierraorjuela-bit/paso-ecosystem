from django.core.management.base import BaseCommand
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
            send_telegram_message(f"🗑️ *Cuenta Desactivada (24h)*\nUsuario: {user.username}")

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
            f"✅ Ejecución Finalizada:\n"
            f"- Morosos desactivados: {count_soft}\n"
            f"- Morosos eliminados: {count_hard}\n"
            f"- Citas liberadas: {count_apps}"
        ))
