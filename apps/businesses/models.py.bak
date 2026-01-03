from django.db import models
from apps.core_saas.models import User

class Salon(models.Model):
    # --- CAMPOS INYECTADOS ---
    phone = models.CharField(max_length=50, verbose_name='Teléfono', blank=True, default='')
    whatsapp = models.CharField(max_length=50, blank=True, verbose_name='WhatsApp')
    instagram = models.CharField(max_length=100, blank=True, verbose_name='Instagram')
    # -------------------------

    # --- REDES SOCIALES (Agregado automáticamente) ---
    whatsapp = models.CharField(max_length=50, blank=True, default='', verbose_name="WhatsApp", help_text="Ej: +57 300 123 4567")
    instagram = models.CharField(max_length=100, blank=True, default='', verbose_name="Instagram", help_text="Usuario sin @")

    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='salon')
    name = models.CharField(max_length=255, verbose_name="Nombre del Negocio")
    description = models.TextField(verbose_name="Descripción", blank=True)
    address = models.CharField(max_length=255, verbose_name="Dirección Física")
    
    # --- NUEVOS CAMPOS DE LUJO Y REDES ---
    city = models.CharField(max_length=100, verbose_name="Ciudad", default="Tunja")
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name="WhatsApp (sin +)")
    instagram_link = models.URLField(blank=True, verbose_name="Link de Instagram")
    maps_link = models.URLField(blank=True, verbose_name="Link de Google Maps")
    
    # Para la foto de perfil
    image = models.ImageField(upload_to='salons/', blank=True, null=True, verbose_name="Logo del Negocio")

    def __str__(self):
        return self.name

class Service(models.Model):
    duration_minutes = models.IntegerField(default=30, verbose_name='Duración (min)')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField(help_text="Duración en minutos")
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

class OpeningHours(models.Model):
    # Modelo legado para compatibilidad si existía antes, 
    # pero Schedule es el principal ahora.
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    weekday = models.IntegerField()
    from_hour = models.TimeField()
    to_hour = models.TimeField()

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
        return f"Cita de {self.customer_name} en {self.salon.name}"

class SalonSchedule(models.Model):
    salon = models.OneToOneField(Salon, on_delete=models.CASCADE, related_name='schedule')
    monday_open = models.BooleanField(default=True, verbose_name="Lunes")
    tuesday_open = models.BooleanField(default=True, verbose_name="Martes")
    wednesday_open = models.BooleanField(default=True, verbose_name="Miércoles")
    thursday_open = models.BooleanField(default=True, verbose_name="Jueves")
    friday_open = models.BooleanField(default=True, verbose_name="Viernes")
    saturday_open = models.BooleanField(default=True, verbose_name="Sábado")
    sunday_open = models.BooleanField(default=False, verbose_name="Domingo")

    def __str__(self):
        return f"Horario de {self.salon.name}"
