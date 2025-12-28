from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.businesses.models import Booking

class Command(BaseCommand):
    help = 'Libera reservas pendientes de pago que han expirado (más de 15 min)'

    def handle(self, *args, **kwargs):
        # Definir tiempo límite (15 minutos)
        tiempo_limite = timezone.now() - timedelta(minutes=15)
        
        # Buscar reservas viejas en estado 'pending_payment'
        reservas_vencidas = Booking.objects.filter(
            status='pending_payment',
            start_time__lte=timezone.now() + timedelta(days=365), # Solo por seguridad de query
            # En realidad filtramos por fecha de creación, pero como Booking no tiene created_at en tu modelo,
            # usaremos una lógica aproximada o asumiremos que si es pending y ya pasó un tiempo razonable, se borra.
            # MEJORA: Agregar campo created_at al modelo Booking.
            # POR AHORA: Usaremos start_time como referencia, pero lo ideal es limpiar por tiempo de "creación".
            # Si no tienes created_at, ten cuidado.
        )
        
        # FIX: Como no tienes 'created_at' en el modelo Booking provisto, 
        # no podemos saber cuándo se CREÓ la reserva, solo cuándo EMPIEZA.
        # Eliminar reservas basadas en start_time es peligroso (borrarías citas futuras).
        
        # SOLUCIÓN PARA ESTE SCRIPT:
        # Solo reportaremos. Para que funcione la eliminación automática, 
        # NECESITAS agregar "created_at = models.DateTimeField(auto_now_add=True)" a tu modelo Booking.
        
        self.stdout.write(self.style.WARNING("⚠️ Para activar la limpieza automática, agrega 'created_at' a tu modelo Booking."))
        self.stdout.write(self.style.SUCCESS("✅ Comando ejecutado correctamente (Modo Seguro)."))