from django.db import models
from django.conf import settings

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_salon')
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Configuración de Horario del Negocio
    opening_time = models.TimeField()
    closing_time = models.TimeField() # Maneja lógica nocturna si close < open
    
    deposit_percentage = models.IntegerField(default=50, help_text="Porcentaje de abono requerido")
    
    # Redes para el Marketplace
    instagram_url = models.URLField(blank=True)
    google_maps_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    duration_minutes = models.IntegerField(help_text="Duración en minutos")
    buffer_time = models.IntegerField(default=15, help_text="Tiempo de limpieza post-servicio")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} - {self.salon.name}"

class EmployeeSchedule(models.Model):
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedule')
    # Aquí irían los JSON o campos para los horarios por día (Lunes a Domingo)
    # Por simplicidad inicial, dejamos el placeholder
    is_active_today = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Horario de {self.employee.username}"