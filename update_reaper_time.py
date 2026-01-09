import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

reaper_content = """
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import User
from apps.marketplace.models import Appointment
from datetime import timedelta

class Command(BaseCommand):
    help = 'El Reaper: Elimina cuentas no pagadas > 24h y citas pendientes > 120min'

    def handle(self, *args, **kwargs):
        # 1. Eliminar Dueños Morosos (24 horas)
        limit_time_owners = timezone.now() - timedelta(hours=24)
        expired_owners = User.objects.filter(role='OWNER', is_verified_payment=False, registration_timestamp__lt=limit_time_owners)
        owners_count = expired_owners.count()
        expired_owners.delete()
        
        # 2. ELIMINAR CITAS PENDIENTES (> 120 MIN / 2 HORAS)
        # CAMBIO AQUI: De 60 a 120 minutos
        limit_time_apps = timezone.now() - timedelta(minutes=120)
        expired_apps = Appointment.objects.filter(status='PENDING', created_at__lt=limit_time_apps)
        apps_count = expired_apps.count()
        expired_apps.delete()
        
        self.stdout.write(self.style.SUCCESS(f'Reaper Reporte: {owners_count} dueños eliminados, {apps_count} citas liberadas (Criterio: 2 Horas).'))
"""

def apply_reaper_update():
    print("⏳ EXTENDIENDO TIEMPO DEL REAPER A 2 HORAS...")
    path = BASE_DIR / 'apps' / 'core' / 'management' / 'commands' / 'run_reaper.py'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(reaper_content.strip())
    print("✅ Reaper actualizado: Ahora espera 120 minutos antes de borrar.")

if __name__ == "__main__":
    apply_reaper_update()