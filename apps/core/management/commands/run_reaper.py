from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import User
from datetime import timedelta

class Command(BaseCommand):
    help = 'El Reaper: Elimina cuentas no pagadas > 24h y citas pendientes > 60min'

    def handle(self, *args, **kwargs):
        # 1. Eliminar Dueños Morosos
        limit_time = timezone.now() - timedelta(hours=24)
        expired_owners = User.objects.filter(role='OWNER', is_verified_payment=False, registration_timestamp__lt=limit_time)
        count = expired_owners.count()
        expired_owners.delete() # O usar is_active = False como sugeriste
        self.stdout.write(self.style.SUCCESS(f'Reaper: {count} cuentas eliminadas.'))
        
        # 2. Aquí iría la lógica para eliminar citas pendientes (cuando creemos el modelo Appointment)