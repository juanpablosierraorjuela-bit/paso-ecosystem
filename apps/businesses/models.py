from django.db import models
from django.conf import settings

class BusinessProfile(models.Model):
    """El Cerebro del Negocio. Vinculado al usuario OWNER."""
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business_profile')
    business_name = models.CharField("Nombre del Negocio", max_length=150)
    description = models.TextField("Descripción", blank=True, help_text="Para el buscador semántico")
    
    address = models.CharField("Dirección Física", max_length=255)
    google_maps_url = models.URLField("Link Google Maps", blank=True)
    
    deposit_percentage = models.PositiveIntegerField("Porcentaje de Abono", default=30)
    is_open_manually = models.BooleanField("Abierto Manualmente", default=True)

    def __str__(self):
        return self.business_name

class Service(models.Model):
    """Catálogo de Servicios Inteligente."""
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='services')
    name = models.CharField("Nombre del Servicio", max_length=100)
    description = models.TextField("Descripción / Palabras Clave")
    
    duration_minutes = models.PositiveIntegerField("Duración (min)")
    buffer_minutes = models.PositiveIntegerField("Tiempo de Limpieza (min)", default=10)
    
    price = models.DecimalField("Precio (COP)", max_digits=10, decimal_places=0)
    is_active = models.BooleanField(default=True)

    def total_duration(self):
        return self.duration_minutes + self.buffer_minutes

    def __str__(self):
        return f"{self.name} - ${self.price}"

class OperatingHour(models.Model):
    """Horario del Local. Soporta turnos de madrugada."""
    DAYS = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'),
        (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo'),
    ]
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='operating_hours')
    day_of_week = models.IntegerField(choices=DAYS)
    opening_time = models.TimeField("Apertura")
    closing_time = models.TimeField("Cierre")
    is_closed = models.BooleanField("Cerrado este día", default=False)

    class Meta:
        ordering = ['day_of_week']
        unique_together = ('business', 'day_of_week')

    def crosses_midnight(self):
        return self.closing_time < self.opening_time

    def __str__(self):
        status = "Cerrado" if self.is_closed else f"{self.opening_time} - {self.closing_time}"
        return f"{self.get_day_of_week_display()}: {status}"
