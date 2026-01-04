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

    def __str__(self):
        return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField(default=30, verbose_name="Duración (min)")
    buffer_time = models.IntegerField(default=0, verbose_name="Tiempo de Limpieza (Buffer)")
    price = models.DecimalField(max_digits=10, decimal_places=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

class Employee(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='employees')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile', null=True, blank=True)
    name = models.CharField(max_length=255) # Unificamos first/last name para simplificar
    phone = models.CharField(max_length=50, blank=True)
    instagram_handle = models.CharField(max_length=50, blank=True, verbose_name="Usuario Instagram")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class SalonSchedule(models.Model):
    salon = models.OneToOneField(Salon, on_delete=models.CASCADE, related_name='schedule')
    # Simplificamos: Guardamos booleano si abre, luego podemos refinar horas
    monday_open = models.BooleanField(default=True)
    tuesday_open = models.BooleanField(default=True)
    wednesday_open = models.BooleanField(default=True)
    thursday_open = models.BooleanField(default=True)
    friday_open = models.BooleanField(default=True)
    saturday_open = models.BooleanField(default=True)
    sunday_open = models.BooleanField(default=False)

class EmployeeSchedule(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='schedule')
    # Formato Texto Simple: "09:00-18:00" o "CERRADO"
    monday_hours = models.CharField(max_length=50, default="09:00-18:00")
    tuesday_hours = models.CharField(max_length=50, default="09:00-18:00")
    wednesday_hours = models.CharField(max_length=50, default="09:00-18:00")
    thursday_hours = models.CharField(max_length=50, default="09:00-18:00")
    friday_hours = models.CharField(max_length=50, default="09:00-18:00")
    saturday_hours = models.CharField(max_length=50, default="09:00-18:00")
    sunday_hours = models.CharField(max_length=50, default="CERRADO")

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING_PAYMENT', 'Pendiente de Pago'), # Naranja Oscuro (60 min timer)
        ('IN_REVIEW', 'En Revisión'),             # Naranja Claro (Cliente envió comprobante)
        ('VERIFIED', 'Verificado'),               # Verde (Dueño confirmó dinero)
        ('COMPLETED', 'Completado'),              # Azul (Servicio realizado)
        ('CANCELLED', 'Cancelado'),               # Rojo
    )
    
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    
    # Datos del Cliente (Registro Lazy)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    customer_email = models.EmailField(blank=True, null=True)
    
    # Datos de la Cita
    date_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True) # Para calculo de traslape
    
    # Datos Financieros
    total_price = models.DecimalField(max_digits=10, decimal_places=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_PAYMENT')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.end_time and self.service:
            # Calcular hora fin automágicamente: Inicio + Duración + Buffer
            duration = self.service.duration + self.service.buffer_time
            self.end_time = self.date_time + timedelta(minutes=duration)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cita #{self.id} - {self.customer_name}"
