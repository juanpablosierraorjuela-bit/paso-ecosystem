from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.businesses.models import BusinessProfile

class Command(BaseCommand):
    help = 'Desactiva suscripciones vencidas automáticamente'

    def handle(self, *args, **kwargs):
        hoy = timezone.now().date()
        self.stdout.write(f"🔍 Revisando vencimientos al: {hoy}")
        
        # Buscar negocios activos con fecha vencida
        vencidos = BusinessProfile.objects.filter(
            is_active_subscription=True, 
            subscription_end_date__lt=hoy
        )
        
        count = vencidos.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✅ Todo en orden. No hay cuentas por vencer.'))
            return

        self.stdout.write(f'⚠️ Encontrados {count} negocios vencidos. Procesando...')

        for negocio in vencidos:
            negocio.is_active_subscription = False
            negocio.save()
            self.stdout.write(self.style.WARNING(f'   🚫 Bloqueado: {negocio.business_name} (Venció: {negocio.subscription_end_date})'))

        self.stdout.write(self.style.SUCCESS(f'🏁 Proceso terminado. {count} cuentas suspendidas.'))
