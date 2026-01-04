from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salon')
    name = models.CharField(max_length=255, verbose_name="Nombre del Negocio")
    description = models.TextField(verbose_name="Descripción", blank=True)
    city = models.CharField(max_length=100, verbose_name="Ciudad", default="Bogotá")
    address = models.CharField(max_length=255, verbose_name="Dirección Física")
    whatsapp_number = models.CharField(max_length=50, blank=True, verbose_name="WhatsApp")
    instagram_link = models.URLField(blank=True, verbose_name="Link Instagram")
    maps_link = models.URLField(blank=True, verbose_name="Link Maps")
    
    # NUEVO: Configuración de Abonos
    deposit_percentage = models.IntegerField(default=50, verbose_name="% de Abono (Ej: 50)")
    
    # NUEVO: Horario General del Negocio (Apertura/Cierre Global)
    opening_time = models.TimeField(default="08:00", verbose_name="Apertura Global")
    closing_time = models.TimeField(default="20:00", verbose_name="Cierre Global")

    def __str__(self):
        return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField(default=30, verbose_name="Duración (min)")
    buffer_time = models.IntegerField(default=10, verbose_name="Limpieza (min)")
    price = models.DecimalField(max_digits=10, decimal_places=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

class Employee(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='employees')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile', null=True, blank=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class EmployeeSchedule(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='schedule')
    # Horarios por día (Texto simple para flexibilidad: "09:00-18:00")
    monday_hours = models.CharField(max_length=50, default="09:00-18:00")
    tuesday_hours = models.CharField(max_length=50, default="09:00-18:00")
    wednesday_hours = models.CharField(max_length=50, default="09:00-18:00")
    thursday_hours = models.CharField(max_length=50, default="09:00-18:00")
    friday_hours = models.CharField(max_length=50, default="09:00-18:00")
    saturday_hours = models.CharField(max_length=50, default="09:00-18:00")
    sunday_hours = models.CharField(max_length=50, default="CERRADO")
    
    # NUEVO: Hora de Almuerzo (Bloqueo Sagrado)
    lunch_start = models.TimeField(null=True, blank=True, verbose_name="Inicio Almuerzo")
    lunch_end = models.TimeField(null=True, blank=True, verbose_name="Fin Almuerzo")

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING_PAYMENT', 'Pendiente de Abono'), # Amarillo
        ('VERIFIED', 'Confirmada'),                # Verde
        ('COMPLETED', 'Completada'),               # Azul
        ('CANCELLED', 'Cancelada'),                # Rojo
    )
    
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    
    # Datos Cliente
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    
    # Datos Tiempo
    date_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # Datos Dinero
    total_price = models.DecimalField(max_digits=10, decimal_places=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_PAYMENT')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Calcular fin de cita automáticamente
        if not self.end_time and self.service:
            total_min = self.service.duration + self.service.buffer_time
            self.end_time = self.date_time + timedelta(minutes=total_min)
        # Calcular abono automático según porcentaje del salón
        if not self.deposit_amount and self.salon:
            percentage = self.salon.deposit_percentage / 100
            self.deposit_amount = self.total_price * percentage
        super().save(*args, **kwargs)
