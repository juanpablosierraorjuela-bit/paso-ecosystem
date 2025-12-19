import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
import datetime

# --- MODELO SALON ---
class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salon')
    name = models.CharField(max_length=200, verbose_name="Nombre del Negocio")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Token para invitar empleados
    invite_token = models.UUIDField(default=uuid.uuid4, editable=False)
    
    # UBICACIÓN
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    address = models.CharField(max_length=255, verbose_name="Dirección")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    
    latitude = models.FloatField(default=0.0, blank=True)
    longitude = models.FloatField(default=0.0, blank=True)

    # IMÁGENES
    logo = models.ImageField(upload_to='salons/logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='salons/banners/', blank=True, null=True)

    # REDES SOCIALES
    instagram = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)

    # INTEGRACIONES
    bold_api_key = models.CharField(max_length=255, blank=True)
    bold_signing_key = models.CharField(max_length=255, blank=True)
    telegram_bot_token = models.CharField(max_length=255, blank=True)
    telegram_chat_id = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if Salon.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{uuid.uuid4().hex[:4]}"
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        now = timezone.localtime(timezone.now())
        current_day = now.weekday()
        current_time = now.time()
        try:
            today_schedule = self.opening_hours.filter(weekday=current_day).first()
            if not today_schedule or today_schedule.is_closed:
                return False
            return today_schedule.from_hour <= current_time <= today_schedule.to_hour
        except Exception:
            return False

    def __str__(self):
        return self.name

# --- MODELO SERVICIOS (Con campo description agregado) ---
class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100, verbose_name="Nombre del Servicio")
    description = models.TextField(blank=True, verbose_name="Descripción")
    duration_minutes = models.PositiveIntegerField(default=30, verbose_name="Duración (min)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")

    def __str__(self):
        return f"{self.name} - ${self.price}"

# --- MODELO EMPLEADOS ---
class Employee(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='employees')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='employee')
    name = models.CharField(max_length=100, default="Empleado")
    phone = models.CharField(max_length=20, default="")
    lunch_start = models.TimeField(default=datetime.time(12, 0))
    lunch_end = models.TimeField(default=datetime.time(13, 0))
    
    bold_api_key = models.CharField(max_length=255, blank=True)
    bold_signing_key = models.CharField(max_length=255, blank=True)
    telegram_bot_token = models.CharField(max_length=255, blank=True)
    telegram_chat_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

# --- HORARIOS ---
class OpeningHours(models.Model):
    WEEKDAYS = [
        (0, "Lunes"), (1, "Martes"), (2, "Miércoles"), (3, "Jueves"),
        (4, "Viernes"), (5, "Sábado"), (6, "Domingo"),
    ]
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='opening_hours')
    weekday = models.IntegerField(choices=WEEKDAYS)
    from_hour = models.TimeField()
    to_hour = models.TimeField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('weekday', 'from_hour')
        unique_together = ('salon', 'weekday')

# --- RESERVAS ---
class Booking(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='my_bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, default='confirmed')

class EmployeeSchedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='schedules')
    weekday = models.IntegerField(choices=OpeningHours.WEEKDAYS)
    from_hour = models.TimeField()
    to_hour = models.TimeField()
    is_closed = models.BooleanField(default=False)