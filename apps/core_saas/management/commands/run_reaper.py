from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core_saas.models import User
from apps.marketplace.models import Appointment
from datetime import timedelta

class Command(BaseCommand):
    help = 'Ejecuta la limpieza automática de usuarios morosos y citas expiradas'

    def handle(self, *args, **kwargs):
        # 1. DUEÑOS MOROSOS (> 24 horas sin verificar pago)
        limit_owners = timezone.now() - timedelta(hours=24)
        owners_to_purge = User.objects.filter(role='OWNER', is_verified_payment=False, registration_timestamp__lt=limit_owners)
        count_owners = owners_to_purge.count()
        owners_to_purge.delete() # O marcar is_active=False para papelera
        
        # 2. CITAS NO ABONADAS (> 60 minutos)
        limit_appointments = timezone.now() - timedelta(minutes=60)
        appointments_to_cancel = Appointment.objects.filter(status='PENDING', created_at__lt=limit_appointments)
        count_apps = appointments_to_cancel.count()
        appointments_to_cancel.update(status='CANCELLED') # O delete()

        self.stdout.write(self.style.SUCCESS(f'Reaper ejecutado: {count_owners} dueños eliminados, {count_apps} citas canceladas.'))