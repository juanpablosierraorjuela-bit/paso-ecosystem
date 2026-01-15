from django.db import models
from django.conf import settings

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_salon')
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    
    # NUEVO: Días que abre el negocio (0=Lunes)
    active_days = models.CharField(max_length=20, default="0,1,2,3,4,5") 
    
    deposit_percentage = models.IntegerField(default=50)
    instagram_url = models.URLField(blank=True)
    google_maps_url = models.URLField(blank=True)

    # NUEVOS CAMPOS PARA PAGOS
    bank_name = models.CharField(max_length=100, blank=True, verbose_name="Nombre del Banco")
    account_number = models.CharField(max_length=50, blank=True, verbose_name="Número de Cuenta")

    def __str__(self):
        return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    duration_minutes = models.IntegerField(help_text="Duración en minutos")
    buffer_time = models.IntegerField(default=15, help_text="Limpieza (min)")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} - {self.salon.name}"

class EmployeeSchedule(models.Model):
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedule')
    work_start = models.TimeField(default='09:00')
    work_end = models.TimeField(default='18:00')
    lunch_start = models.TimeField(default='13:00')
    lunch_end = models.TimeField(default='14:00')
    active_days = models.CharField(max_length=20, default="0,1,2,3,4,5") 
    is_active_today = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Horario de {self.employee.username}"