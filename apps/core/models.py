from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrador PASO"
        OWNER = "OWNER", "Dueño de Negocio"
        EMPLOYEE = "EMPLOYEE", "Empleado / Especialista"
        CLIENT = "CLIENT", "Cliente Final"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CLIENT)
    phone = models.CharField("Teléfono / WhatsApp", max_length=20, blank=True, null=True)
    city = models.CharField("Ciudad", max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified_payment = models.BooleanField("Pago Mensualidad Verificado", default=False)
    registration_timestamp = models.DateTimeField("Fecha de Registro", auto_now_add=True)
    instagram_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class PlatformSettings(models.Model):
    """
    Modelo Único para controlar las variables globales del ecosistema.
    Solo puede existir UNA instancia de este modelo.
    """
    site_name = models.CharField("Nombre del Sitio", max_length=100, default="PASO Ecosistema")
    support_whatsapp = models.CharField("WhatsApp de Soporte (Tú)", max_length=20, help_text="Donde los dueños envían los comprobantes")
    
    # TELEGRAM CONFIG
    telegram_bot_token = models.CharField("Token del Bot de Telegram", max_length=200, blank=True)
    telegram_chat_id = models.CharField("Tu Chat ID de Telegram", max_length=100, blank=True)
    
    # REDES SOCIALES (Footer)
    instagram_link = models.URLField("Instagram PASO", blank=True)
    facebook_link = models.URLField("Facebook PASO", blank=True)
    linkedin_link = models.URLField("LinkedIn PASO", blank=True)

    class Meta:
        verbose_name = "⚙️ Configuración del Ecosistema"
        verbose_name_plural = "⚙️ Configuración del Ecosistema"

    def save(self, *args, **kwargs):
        if not self.pk and PlatformSettings.objects.exists():
            raise ValidationError('Solo puede existir una configuración global.')
        return super(PlatformSettings, self).save(*args, **kwargs)

    def __str__(self):
        return "Configuración Principal PASO"
