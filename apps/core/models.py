from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrador PASO"
        OWNER = "OWNER", "Dueño de Negocio"
        EMPLOYEE = "EMPLOYEE", "Empleado / Especialista"
        CLIENT = "CLIENT", "Cliente Final"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CLIENT)
    
    # Datos de Contacto
    phone = models.CharField("Teléfono / WhatsApp", max_length=20, blank=True, null=True)
    city = models.CharField("Ciudad", max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    instagram_link = models.URLField("Perfil de Instagram", blank=True, null=True)
    
    # Vinculación Laboral
    workplace = models.ForeignKey('businesses.Salon', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')

    # Lógica de Seguridad
    is_verified_payment = models.BooleanField("Pago Mensualidad Verificado", default=False)
    registration_timestamp = models.DateTimeField("Fecha de Registro", auto_now_add=True)
    is_active_account = models.BooleanField("Cuenta Activa", default=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    # --- AQUÍ ESTÁ LA FÓRMULA MÁGICA QUE FALTABA ---
    @property
    def hours_since_registration(self):
        if not self.registration_timestamp:
            return 0
        delta = timezone.now() - self.registration_timestamp
        return delta.total_seconds() / 3600

class PlatformSettings(models.Model):
    site_name = models.CharField("Nombre del Sitio", max_length=100, default="PASO Ecosistema")
    support_whatsapp = models.CharField("WhatsApp de Soporte", max_length=20)
    telegram_bot_token = models.CharField(max_length=200, blank=True)
    telegram_chat_id = models.CharField(max_length=100, blank=True)
    instagram_link = models.URLField(blank=True)
    facebook_link = models.URLField(blank=True)
    linkedin_link = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and PlatformSettings.objects.exists():
            raise ValidationError('Solo puede existir una configuración global.')
        return super(PlatformSettings, self).save(*args, **kwargs)
