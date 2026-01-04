from django.db import models
from apps.core_saas.models import User

class Salon(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='salon')
    name = models.CharField(max_length=255, verbose_name="Nombre del Negocio")
    description = models.TextField(verbose_name="Descripción", blank=True)
    address = models.CharField(max_length=255, verbose_name="Dirección Física")
    
    # --- CAMPOS DE LUJO Y REDES (SIN IMAGEN) ---
    city = models.CharField(max_length=100, verbose_name="Ciudad", default="Tunja")
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name="WhatsApp (Ej: 573001234567)")
    instagram_link = models.URLField(blank=True, verbose_name="Link de Instagram")
    maps_link = models.URLField(blank=True, verbose_name="Link de Google Maps")
    
    # Eliminamos el campo ImageField para evitar problemas y mantener el diseño de iniciales

    def __str__(self):
        return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField(help_text="Duración en minutos", verbose_name="Duración (min)")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.salon.name}"

class Employee(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Schedule(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=[
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), 
        (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmada'),
        ('COMPLETED', 'Completada'),
        ('CANCELLED', 'Cancelada'),
    )
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True)
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cita de {self.customer_name}"
