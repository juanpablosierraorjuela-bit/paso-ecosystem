from django.db import models
from django.conf import settings

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente de Abono'),
        ('VERIFIED', 'Verificada'),
        ('COMPLETED', 'Completada'),
        ('CANCELLED', 'Cancelada'),
    )
    
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    salon = models.ForeignKey('businesses.Salon', on_delete=models.CASCADE)
    # Cambio: Ahora una cita puede tener múltiples servicios (Combo)
    services = models.ManyToManyField('businesses.Service', related_name='appointments')
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='work_appointments')
    
    date_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Cita {self.id} - {self.client.username}"