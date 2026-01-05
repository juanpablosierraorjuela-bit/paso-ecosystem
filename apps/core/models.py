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
    
    # --- Datos de Contacto y Perfil ---
    phone = models.CharField("Teléfono / WhatsApp", max_length=20, blank=True, null=True)
    city = models.CharField("Ciudad", max_length=100, blank=True, null=True, help_text="Ciudad seleccionada del dropdown")
    
    # Imagen: Si está vacía, el Template generará el avatar de lujo con iniciales
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Redes Sociales Personales
    instagram_link = models.URLField("Perfil de Instagram", blank=True, null=True)
    
    # --- Lógica de Seguridad y Pagos (El Ciclo de 24h) ---
    is_verified_payment = models.BooleanField("Pago Mensualidad Verificado", default=False, help_text="Si es Falso pasadas 24h, el sistema lo eliminará.")
    registration_timestamp = models.DateTimeField("Fecha de Registro", auto_now_add=True)
    
    # Soft Delete
    is_active_account = models.BooleanField("Cuenta Activa", default=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def hours_since_registration(self):
        delta = timezone.now() - self.registration_timestamp
        return delta.total_seconds() / 3600

class PlatformSettings(models.Model):
    """Configuración Global del Sistema."""
    site_name = models.CharField("Nombre del Sitio", max_length=100, default="PASO Ecosistema")
    support_whatsapp = models.CharField("WhatsApp de Soporte", max_length=20, help_text="Número para comprobantes")
    
    # --- Conexión Telegram ---
    telegram_bot_token = models.CharField("Token Bot Telegram", max_length=200, blank=True)
    telegram_chat_id = models.CharField("Chat ID Telegram", max_length=100, blank=True)
    
    # --- Footer Dinámico ---
    instagram_link = models.URLField("Instagram PASO", blank=True)
    facebook_link = models.URLField("Facebook PASO", blank=True)
    linkedin_link = models.URLField("LinkedIn PASO", blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and PlatformSettings.objects.exists():
            raise ValidationError('Solo puede existir una configuración global.')
        return super(PlatformSettings, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "⚙️ Configuración del Ecosistema"
        verbose_name_plural = "⚙️ Configuración del Ecosistema"
