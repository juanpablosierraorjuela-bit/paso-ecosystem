from django.db import models
from django.conf import settings

class Salon(models.Model):

    # --- REDES SOCIALES (Protocolo Diamante) ---
    instagram_url = models.URLField(max_length=200, blank=True, null=True, verbose_name="Enlace de Instagram")
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número de WhatsApp")

    # Campos básicos
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salons', null=True, blank=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    
    # --- NUEVOS CAMPOS (INTEGRACIONES) ---
    # Horarios
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    
    # Telegram
    telegram_bot_token = models.CharField(max_length=200, blank=True, null=True)
    telegram_chat_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Bold & Pagos
    bold_identity_key = models.CharField(max_length=200, blank=True, null=True)
    bold_secret_key = models.CharField(max_length=200, blank=True, null=True)
    deposit_percentage = models.IntegerField(default=100, help_text="Porcentaje a cobrar online (0-100)")

    def __str__(self):
        return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    duration_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name

class EmployeeSchedule(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    weekday = models.IntegerField(choices=[
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'),
        (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')
    ])
    from_hour = models.TimeField()
    to_hour = models.TimeField()
    is_active = models.BooleanField(default=True)

class Booking(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='bookings', blank=True)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    
    # Control Financiero y Estado
    status = models.CharField(max_length=20, default='confirmed')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_id = models.CharField(max_length=100, blank=True, null=True) # Referencia Bold
