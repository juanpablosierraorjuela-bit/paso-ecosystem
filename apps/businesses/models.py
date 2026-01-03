from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone

class Salon(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_salons')
    name = models.CharField(max_length=255, verbose_name="Nombre del Negocio")
    slug = models.SlugField(unique=True, blank=True)
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    address = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    phone = models.CharField(max_length=50, verbose_name="WhatsApp del Negocio")
    instagram_link = models.URLField(blank=True, null=True, verbose_name="Link de Instagram")
    deposit_percentage = models.IntegerField(default=30, verbose_name="% de Abono")
    description = models.TextField(blank=True, verbose_name="Descripción")

    # Horarios Generales
    open_time = models.TimeField(default='08:00', verbose_name="Apertura")
    close_time = models.TimeField(default='20:00', verbose_name="Cierre")

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + '-' + str(self.owner.id)[:4]
        super().save(*args, **kwargs)

    def __str__(self): return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    duration_minutes = models.IntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self): return f"{self.name} (${self.price})"

class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    instagram_link = models.URLField(blank=True, null=True)

    # Horario Almuerzo (Simple)
    lunch_start = models.TimeField(null=True, blank=True)
    lunch_end = models.TimeField(null=True, blank=True)

    def __str__(self): return self.name

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', '🟡 Pendiente Abono'),
        ('in_review', '🟠 En Revisión'),
        ('confirmed', '🟢 Confirmada'),
        ('cancelled', '🔴 Cancelada'),
        ('expired', '⚫ Expirada'),
    ]

    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=50)

    date = models.DateField()
    time = models.TimeField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"Cita #{self.id} - {self.customer_name}"