from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import requests

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERUSER = "ADMIN", "Arquitecto PASO"
        OWNER = "OWNER", "Dueño de Negocio"
        EMPLOYEE = "EMPLOYEE", "Talento / Empleado"
        CLIENT = "CLIENT", "Cliente Final"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CLIENT)
    phone = models.CharField("WhatsApp", max_length=20, blank=True)
    city = models.CharField("Ciudad", max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Lógica de "El Reaper" (Cobro 24h)
    is_verified_payment = models.BooleanField("Pago Verificado ($50k)", default=False)
    registration_timestamp = models.DateTimeField(auto_now_add=True)
    
    # Vinculación Laboral (Para empleados)
    workplace = models.ForeignKey('businesses.Salon', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')

    def hours_since_registration(self):
        delta = timezone.now() - self.registration_timestamp
        return delta.total_seconds() / 3600

class GlobalSettings(models.Model):
    site_name = models.CharField(max_length=100, default="PASO Ecosistema")
    support_whatsapp = models.CharField(max_length=20, default="573000000000")
    telegram_token = models.CharField(max_length=200, blank=True)
    telegram_chat_id = models.CharField(max_length=100, blank=True)
    instagram_link = models.URLField(blank=True)
    facebook_link = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and GlobalSettings.objects.exists():
            return # Singleton
        super().save(*args, **kwargs)
        
    def send_telegram_test(self):
        if self.telegram_token and self.telegram_chat_id:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {"chat_id": self.telegram_chat_id, "text": "🚀 PASO Ecosistema: Conexión Exitosa"}
            requests.post(url, data=data)