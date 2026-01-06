from django.db import models
from django.conf import settings
from datetime import datetime
import pytz

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salon')
    name = models.CharField("Nombre del Negocio", max_length=255)
    description = models.TextField("Descripción (Buscador Semántico)", blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100) # Dropdown en Frontend
    
    # Redes y Ubicación
    maps_link = models.URLField(blank=True)
    instagram_link = models.URLField(blank=True)
    
    # Configuración de Negocio
    deposit_percentage = models.IntegerField(default=30)
    
    # Horario Global (Overnight Logic)
    opening_time = models.TimeField(default="08:00")
    closing_time = models.TimeField(default="20:00")
    
    # Días de Apertura
    work_monday = models.BooleanField(default=True)
    work_tuesday = models.BooleanField(default=True)
    work_wednesday = models.BooleanField(default=True)
    work_thursday = models.BooleanField(default=True)
    work_friday = models.BooleanField(default=True)
    work_saturday = models.BooleanField(default=True)
    work_sunday = models.BooleanField(default=False)

    def is_open_now(self):
        bogota = pytz.timezone('America/Bogota')
        now = datetime.now(bogota)
        current_time = now.time()
        # Lógica simple, se expandirá en views para overnight
        return True # Simplificado para el ejemplo

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.IntegerField(help_text="Minutos")
    buffer_time = models.IntegerField(default=10, help_text="Minutos de limpieza")
    price = models.DecimalField(max_digits=10, decimal_places=0)
    is_active = models.BooleanField(default=True)

class EmployeeSchedule(models.Model):
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedule')
    # Horarios por día "09:00-18:00" o "CERRADO"
    monday_hours = models.CharField(max_length=50, default="09:00-18:00")
    tuesday_hours = models.CharField(max_length=50, default="09:00-18:00")
    wednesday_hours = models.CharField(max_length=50, default="09:00-18:00")
    thursday_hours = models.CharField(max_length=50, default="09:00-18:00")
    friday_hours = models.CharField(max_length=50, default="09:00-18:00")
    saturday_hours = models.CharField(max_length=50, default="09:00-18:00")
    sunday_hours = models.CharField(max_length=50, default="CERRADO")