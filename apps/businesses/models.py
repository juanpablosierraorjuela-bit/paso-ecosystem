from django.db import models
from apps.core_saas.models import User

class Salon(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='salon')
    name = models.CharField(max_length=255, verbose_name="Nombre del Negocio")
    description = models.TextField(verbose_name="Descripción", blank=True)
    city = models.CharField(max_length=100, verbose_name="Ciudad", default="Bogotá")
    address = models.CharField(max_length=255, verbose_name="Dirección Física")
    
    # Redes y Contacto (Nombres correctos para los templates nuevos)
    whatsapp_number = models.CharField(max_length=50, blank=True, verbose_name="WhatsApp")
    instagram_link = models.URLField(blank=True, verbose_name="Link Instagram")
    maps_link = models.URLField(blank=True, verbose_name="Link Maps")

    def __str__(self):
        return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField(default=30, verbose_name="Duración (min)")
    price = models.DecimalField(max_digits=10, decimal_places=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.salon.name}"

class Employee(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# Modelo simple de Citas para que el botón Reservar funcione
class Booking(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    date_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='PENDING')
