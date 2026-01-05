from django.db import models
from django.conf import settings
from apps.businesses.models import BusinessProfile, Service

class EmployeeSchedule(models.Model):
    """
    Capa 2 de Disponibilidad: Horario del Empleado.
    Subordinado al horario del negocio.
    """
    DAYS = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'),
        (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo'),
    ]
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules')
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE) 
    
    day_of_week = models.IntegerField(choices=DAYS)
    start_time = models.TimeField("Entrada")
    end_time = models.TimeField("Salida")
    
    # --- Descansos ---
    break_start = models.TimeField("Inicio Almuerzo", blank=True, null=True)
    break_end = models.TimeField("Fin Almuerzo", blank=True, null=True)
    
    # --- Switch de Emergencia ---
    is_active_day = models.BooleanField("Trabaja hoy", default=True, help_text="Desactivar si el empleado faltó hoy")

    class Meta:
        unique_together = ('employee', 'day_of_week')

class Appointment(models.Model):
    """
    El Corazón Transaccional.
    Maneja el estado PENDING para el cronómetro de 60 minutos.
    """
    STATUS_CHOICES = [
        ('PENDING', '🟡 Pendiente de Abono (60 min)'),
        ('VERIFIED', '🟢 Verificada (Abono Recibido)'),
        ('COMPLETED', '🏁 Completada'),
        ('CANCELLED', '🔴 Cancelada'),
        ('EXPIRED', '⏱️ Expirada (No pagó)'),
    ]

    # Relaciones
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_appointments')
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    # Tiempo
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Estado y Pagos
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True) # Inicio del cronómetro de 60 min
    
    deposit_amount = models.DecimalField("Monto Abono", max_digits=10, decimal_places=0)
    total_price = models.DecimalField("Precio Total", max_digits=10, decimal_places=0)
    
    notes = models.TextField("Notas del Cliente", blank=True)

    def __str__(self):
        return f"Cita {self.id}: {self.client.username} - {self.status}"
