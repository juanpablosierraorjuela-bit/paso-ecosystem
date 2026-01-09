from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import User
from apps.marketplace.models import Appointment
from datetime import timedelta

class Command(BaseCommand):
    help = 'El Reaper: Elimina cuentas no pagadas > 24h y citas pendientes > 60min'

    def handle(self, *args, **kwargs):
        # 1. Eliminar Dueños Morosos
        limit_time_owners = timezone.now() - timedelta(hours=24)
        expired_owners = User.objects.filter(role='OWNER', is_verified_payment=False, registration_timestamp__lt=limit_time_owners)
        owners_count = expired_owners.count()
        expired_owners.delete()
        
        # 2. ELIMINAR CITAS PENDIENTES (> 60 MIN) - ¡AQUÍ ESTÁ LA MAGIA!
        limit_time_apps = timezone.now() - timedelta(minutes=60)
        expired_apps = Appointment.objects.filter(status='PENDING', created_at__lt=limit_time_apps)
        apps_count = expired_apps.count()
        expired_apps.delete()
        
        self.stdout.write(self.style.SUCCESS(f'Reaper Reporte: {owners_count} dueños eliminados, {apps_count} citas liberadas.'))