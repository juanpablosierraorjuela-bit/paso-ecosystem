from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
import pytz

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salon')
    name = models.CharField(max_length=255, verbose_name="Nombre del Negocio")
    description = models.TextField(verbose_name="Descripción", blank=True)
    city = models.CharField(max_length=100, verbose_name="Ciudad", default="Bogotá")
    address = models.CharField(max_length=255, verbose_name="Dirección Física")
    
    whatsapp_number = models.CharField(max_length=50, blank=True, verbose_name="WhatsApp")
    instagram_link = models.URLField(blank=True, verbose_name="Link Instagram")
    maps_link = models.URLField(blank=True, verbose_name="Link Maps")
    
    deposit_percentage = models.IntegerField(default=50, verbose_name="% de Abono")
    
    # Horarios
    opening_time = models.TimeField(default="08:00", verbose_name="Apertura")
    closing_time = models.TimeField(default="20:00", verbose_name="Cierre")
    
    # Días
    work_monday = models.BooleanField(default=True, verbose_name="Lunes")
    work_tuesday = models.BooleanField(default=True, verbose_name="Martes")
    work_wednesday = models.BooleanField(default=True, verbose_name="Miércoles")
    work_thursday = models.BooleanField(default=True, verbose_name="Jueves")
    work_friday = models.BooleanField(default=True, verbose_name="Viernes")
    work_saturday = models.BooleanField(default=True, verbose_name="Sábado")
    work_sunday = models.BooleanField(default=False, verbose_name="Domingo")

    def __str__(self): return self.name

    @property
    def is_open_now(self):
        """Calcula si está abierto (Soporta trasnocho ej: 10pm - 3am)"""
        bogota = pytz.timezone('America/Bogota')
        now = datetime.now(bogota)
        current_time = now.time()
        
        today_idx = now.weekday()
        yesterday_idx = (today_idx - 1) % 7
        
        days_map = [self.work_monday, self.work_tuesday, self.work_wednesday, self.work_thursday, self.work_friday, self.work_saturday, self.work_sunday]
        
        # 1. Turno de HOY
        if days_map[today_idx]:
            if self.opening_time <= self.closing_time:
                # Horario normal (8am - 8pm)
                if self.opening_time <= current_time <= self.closing_time: return True
            else:
                # Horario nocturno (10pm - 3am) -> Si es HOY, debe ser tarde
                if current_time >= self.opening_time: return True
        
        # 2. Turno de AYER (La Madrugada)
        if days_map[yesterday_idx] and self.opening_time > self.closing_time:
            # Si ayer fue nocturno, y hoy es temprano (antes del cierre)
            if current_time <= self.closing_time: return True
            
        return False

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField(default=30)
    buffer_time = models.IntegerField(default=10)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class Employee(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='employees')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile', null=True, blank=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    instagram_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class EmployeeSchedule(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='schedule')
    monday_hours = models.CharField(max_length=50, default="09:00-18:00")
    tuesday_hours = models.CharField(max_length=50, default="09:00-18:00")
    wednesday_hours = models.CharField(max_length=50, default="09:00-18:00")
    thursday_hours = models.CharField(max_length=50, default="09:00-18:00")
    friday_hours = models.CharField(max_length=50, default="09:00-18:00")
    saturday_hours = models.CharField(max_length=50, default="09:00-18:00")
    sunday_hours = models.CharField(max_length=50, default="CERRADO")

class Booking(models.Model):
    STATUS_CHOICES = (('PENDING_PAYMENT', 'Pendiente'), ('VERIFIED', 'Confirmada'), ('COMPLETED', 'Completada'), ('CANCELLED', 'Cancelada'))
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    date_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_PAYMENT')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.end_time and self.service:
            total_min = self.service.duration + self.service.buffer_time
            self.end_time = self.date_time + timedelta(minutes=total_min)
        if not self.deposit_amount and self.salon:
            self.deposit_amount = self.total_price * (self.salon.deposit_percentage / 100)
        super().save(*args, **kwargs)
