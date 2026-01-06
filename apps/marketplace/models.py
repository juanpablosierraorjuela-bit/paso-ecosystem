from django.db import models
from django.conf import settings
from apps.businesses.models import Salon, Service

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente de Abono'), # Cronómetro 60 min
        ('VERIFIED', 'Verificada / Pagada'),
        ('COMPLETED', 'Completada'),
        ('CANCELLED', 'Cancelada'),
    )
    
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='work_appointments')
    
    date_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    total_price = models.DecimalField(max_digits=10, decimal_places=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def minutes_since_creation(self):
        from django.utils import timezone
        delta = timezone.now() - self.created_at
        return delta.total_seconds() / 60