from datetime import time, datetime
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_salon')
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Horarios con valores por defecto seguros
    opening_time = models.TimeField(default=time(9, 0))
    closing_time = models.TimeField(default=time(18, 0))
    
    # Días que abre el negocio (0=Lunes)
    active_days = models.CharField(max_length=20, default="0,1,2,3,4,5") 
    
    deposit_percentage = models.IntegerField(default=50)
    instagram_url = models.URLField(blank=True)
    google_maps_url = models.URLField(blank=True)

    # CAMPOS PARA PAGOS
    bank_name = models.CharField(max_length=100, blank=True, verbose_name="Nombre del Banco")
    account_number = models.CharField(max_length=50, blank=True, verbose_name="Número de Cuenta")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # 1. Corregir días activos si vienen como lista desde el formulario
        if isinstance(self.active_days, list):
            self.active_days = ",".join(self.active_days)
        
        # 2. Forzar conversión de hora si llega como string (evita el fallo de guardado)
        if isinstance(self.opening_time, str):
            try:
                self.opening_time = datetime.strptime(self.opening_time, '%H:%M').time()
            except ValueError:
                pass # Si falla el formato, Django lanzará error de validación normal

        if isinstance(self.closing_time, str):
            try:
                self.closing_time = datetime.strptime(self.closing_time, '%H:%M').time()
            except ValueError:
                pass

        super().save(*args, **kwargs)

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
    work_start = models.TimeField(null=True, blank=True, default=time(9, 0))
    work_end = models.TimeField(null=True, blank=True, default=time(18, 0))
    lunch_start = models.TimeField(null=True, blank=True, default=time(13, 0))
    lunch_end = models.TimeField(null=True, blank=True, default=time(14, 0))
    active_days = models.CharField(max_length=20, default="0,1,2,3,4,5") 
    is_active_today = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Horario Base de {self.employee.username}"

    def save(self, *args, **kwargs):
        if isinstance(self.active_days, list):
            self.active_days = ",".join(self.active_days)
        super().save(*args, **kwargs)

class EmployeeWeeklySchedule(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='weekly_schedules')
    year = models.IntegerField()
    week_number = models.IntegerField()
    work_start = models.TimeField(default=time(9,0))
    work_end = models.TimeField(default=time(18,0))
    lunch_start = models.TimeField(default=time(13,0))
    lunch_end = models.TimeField(default=time(14,0))
    active_days = models.CharField(max_length=100, default="0,1,2,3,4,5") 

    class Meta:
        unique_together = ('employee', 'year', 'week_number')
        ordering = ['year', 'week_number']

    def save(self, *args, **kwargs):
        if isinstance(self.active_days, list):
            self.active_days = ",".join(self.active_days)
        super().save(*args, **kwargs)