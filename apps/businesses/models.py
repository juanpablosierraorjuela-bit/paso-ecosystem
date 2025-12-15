import uuid
import datetime
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone

# --- LÓGICA DE HORARIOS ---
def check_is_open(opening_hours_qs):
    now = timezone.localtime(timezone.now())
    current_day = now.weekday()
    schedule = opening_hours_qs.filter(weekday=current_day, is_closed=False).first()
    if schedule:
        return schedule.from_hour <= now.time() <= schedule.to_hour
    return False

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salon')
    name = models.CharField("Nombre del Negocio", max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    
    city = models.CharField("Ciudad", max_length=100, default="Tunja")
    address = models.CharField("Dirección Física", max_length=255, blank=True)
    phone = models.CharField("Celular", max_length=20, blank=True)
    description = models.TextField("Descripción", blank=True)

    # Campos de Diseño
    latitude = models.FloatField("Latitud", default=0.0)
    longitude = models.FloatField("Longitud", default=0.0)
    instagram = models.URLField("Link Instagram", blank=True)
    facebook = models.URLField("Link Facebook", blank=True)
    tiktok = models.URLField("Link TikTok", blank=True)
    
    # Integraciones Salón
    bold_api_key = models.CharField(max_length=255, blank=True, null=True)
    bold_signing_key = models.CharField(max_length=255, blank=True, null=True)
    telegram_bot_token = models.CharField(max_length=255, blank=True, null=True)
    telegram_chat_id = models.CharField(max_length=255, blank=True, null=True)
    
    invite_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def is_open(self):
        return check_is_open(self.opening_hours.all())

    def __str__(self):
        return self.name

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

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    duration_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='employees')
    specialties = models.ManyToManyField(Service, blank=True)
    
    # Configuración del Empleado (Bold + Telegram)
    bold_api_key = models.CharField("API Key (Bold)", max_length=255, blank=True, null=True)
    bold_signing_key = models.CharField("Signing Key (Bold)", max_length=255, blank=True, null=True)
    
    # NUEVO: Telegram para el empleado
    telegram_bot_token = models.CharField("Telegram Bot Token", max_length=255, blank=True, null=True)
    telegram_chat_id = models.CharField("Telegram Chat ID", max_length=255, blank=True, null=True)
    
    lunch_start = models.TimeField(null=True, blank=True)
    lunch_end = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    def is_working_now(self):
        return check_is_open(self.schedule.all())

    # --- EL CEREBRO DE DISPONIBILIDAD ---
    def is_available(self, date, start_time, duration_minutes):
        service_start = datetime.datetime.combine(date, start_time)
        service_end = service_start + datetime.timedelta(minutes=duration_minutes)
        
        day_schedule = self.schedule.filter(weekday=date.weekday(), is_closed=False).first()
        if not day_schedule: return False, "No trabaja este día."
            
        work_start = datetime.datetime.combine(date, day_schedule.from_hour)
        work_end = datetime.datetime.combine(date, day_schedule.to_hour)
        
        if service_start < work_start or service_end > work_end: return False, "Fuera de horario."

        if self.lunch_start and self.lunch_end:
            l_start = datetime.datetime.combine(date, self.lunch_start)
            l_end = datetime.datetime.combine(date, self.lunch_end)
            if (service_start < l_end and service_end > l_start): return False, "Hora de almuerzo."

        conflicts = self.bookings.filter(start_time__lt=service_end, end_time__gt=service_start, status__in=['pending', 'confirmed'])
        if conflicts.exists(): return False, "Ya tiene otra reserva."

        return True, "Disponible"

class EmployeeSchedule(models.Model):
    WEEKDAYS = [
        (0, "Lunes"), (1, "Martes"), (2, "Miércoles"), (3, "Jueves"),
        (4, "Viernes"), (5, "Sábado"), (6, "Domingo"),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='schedule')
    weekday = models.IntegerField(choices=WEEKDAYS)
    from_hour = models.TimeField()
    to_hour = models.TimeField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('weekday', 'from_hour')
        unique_together = ('employee', 'weekday')

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
    ]
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.customer_name} - {self.service.name}"