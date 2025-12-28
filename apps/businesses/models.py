from django.db import models
from django.conf import settings
from django.utils import timezone # Importación optimizada

class Salon(models.Model):
    # --- REDES SOCIALES (Protocolo Diamante) ---
    instagram_url = models.URLField(max_length=200, blank=True, null=True, verbose_name="Enlace de Instagram")
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número de WhatsApp")

    # Campos básicos
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salons', null=True, blank=True)
    name = models.CharField(max_length=100)
    
    # --- UBICACIÓN REAL (Nivel Marketplace Nacional) ---
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección Física")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

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

    @property
    def is_open_now(self):
        """Determina si el salón está abierto en este momento exacto."""
        if not self.opening_time or not self.closing_time:
            return False
            
        # Obtenemos la hora actual en la zona horaria del servidor
        now = timezone.localtime(timezone.now()).time()
        
        if self.opening_time < self.closing_time:
            # Horario normal (ej: 8am a 8pm)
            return self.opening_time <= now <= self.closing_time
        else:
            # Horario nocturno que cruza medianoche (ej: 6pm a 2am)
            return now >= self.opening_time or now <= self.closing_time
    
    def __str__(self):
        return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    
    # --- UBICACIÓN REAL (Nivel Marketplace Nacional) ---
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección Física")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

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
    
    # --- UBICACIÓN REAL (Nivel Marketplace Nacional) ---
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección Física")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='bookings', blank=True)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    
    # --- AUDITORÍA DE TIEMPO (Vital para Recuperación de Carrito) ---
    created_at = models.DateTimeField(auto_now_add=True) # <--- ¡NUEVO CAMPO CRÍTICO!

    # Control Financiero y Estado
    status = models.CharField(max_length=20, default='confirmed')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_id = models.CharField(max_length=100, blank=True, null=True) # Referencia Bold