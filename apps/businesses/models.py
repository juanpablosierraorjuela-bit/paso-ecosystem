from datetime import time
from django.db import models
from django.conf import settings

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_salon')
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # AJUSTE: Se añade null=True y default para mayor flexibilidad al guardar
    opening_time = models.TimeField(null=True, blank=True, default=time(9, 0))
    closing_time = models.TimeField(null=True, blank=True, default=time(18, 0))
    
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
        # Si active_days llega como lista (desde el formulario de checkboxes), lo unimos con comas
        if isinstance(self.active_days, list):
            self.active_days = ",".join(self.active_days)
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
    """
    Permite configurar horarios específicos para una semana concreta del año.
    Si no existe configuración para una semana, se usa el EmployeeSchedule (base).
    """
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='weekly_schedules')
    year = models.IntegerField()
    week_number = models.IntegerField() # Número de semana ISO (1-52)
    
    # Horarios específicos para esta semana
    work_start = models.TimeField(default=time(9,0))
    work_end = models.TimeField(default=time(18,0))
    lunch_start = models.TimeField(default=time(13,0))
    lunch_end = models.TimeField(default=time(14,0))
    
    # Días activos en esta semana específica (ej: "0,2,4")
    active_days = models.CharField(max_length=100, default="0,1,2,3,4,5") 

    class Meta:
        unique_together = ('employee', 'year', 'week_number')
        ordering = ['year', 'week_number']

    def save(self, *args, **kwargs):
        if isinstance(self.active_days, list):
            self.active_days = ",".join(self.active_days)
        super().save(*args, **kwargs)