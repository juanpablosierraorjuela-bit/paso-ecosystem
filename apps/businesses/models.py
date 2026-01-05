from django.db import models
from django.conf import settings

class BusinessProfile(models.Model):
    """
    El Cerebro del Negocio. Vinculado al usuario OWNER.
    """
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business_profile')
    business_name = models.CharField("Nombre del Negocio", max_length=150)
    description = models.TextField("Descripción", blank=True, help_text="Texto persuasivo para el buscador semántico")
    
    # --- Ubicación ---
    address = models.CharField("Dirección Física", max_length=255)
    google_maps_url = models.URLField("Link Google Maps", blank=True, help_text="Para el botón flotante en la tarjeta")
    
    # --- Configuración Financiera ---
    deposit_percentage = models.PositiveIntegerField("Porcentaje de Abono", default=30, help_text="Porcentaje (0-100) requerido para reservar")
    
    # --- Interruptores de Estado ---
    is_open_manually = models.BooleanField("Abierto Manualmente", default=True, help_text="Switch de emergencia para cerrar el negocio en el Marketplace")

    def __str__(self):
        return self.business_name

class Service(models.Model):
    """
    Catálogo de Servicios Inteligente.
    """
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='services')
    name = models.CharField("Nombre del Servicio", max_length=100)
    description = models.TextField("Descripción / Palabras Clave", help_text="Descripción para búsqueda semántica (Ej: 'Ideal para cabello seco')")
    
    # --- Tiempos ---
    duration_minutes = models.PositiveIntegerField("Duración del Servicio (min)")
    buffer_minutes = models.PositiveIntegerField("Tiempo de Limpieza/Buffer (min)", default=10, help_text="Tiempo muerto entre citas para organizar")
    
    price = models.DecimalField("Precio (COP)", max_digits=10, decimal_places=0)
    is_active = models.BooleanField(default=True)

    def total_duration(self):
        return self.duration_minutes + self.buffer_minutes

    def __str__(self):
        return f"{self.name} - ${self.price}"

class OperatingHour(models.Model):
    """
    Capa 1 de Disponibilidad: Horario del Local.
    Soporta 'Overnight Shift' (Ej: Abre Sábado 10PM -> Cierra Domingo 5AM).
    """
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
        """Devuelve True si el turno termina al día siguiente"""
        return self.closing_time < self.opening_time

    def __str__(self):
        status = "Cerrado" if self.is_closed else f"{self.opening_time} - {self.closing_time}"
        return f"{self.get_day_of_week_display()}: {status}"
