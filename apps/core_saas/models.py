from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Actualizamos ADMIN por OWNER para que coincida con tus vistas
    ROLE_CHOICES = (("CLIENT", "Cliente"), ("OWNER", "Dueño de Negocio"), ("EMPLOYEE", "Empleado"))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="CLIENT")
    phone = models.CharField(max_length=20, blank=True)

class PlatformSettings(models.Model):
    whatsapp_number = models.CharField(max_length=50, blank=True, help_text="Número WhatsApp del soporte")
    instagram_link = models.URLField(blank=True, help_text="Link completo de Instagram")
    
    class Meta:
        verbose_name = "Configuración de Plataforma"
        verbose_name_plural = "Configuración de Plataforma"

    def __str__(self):
        return "Ajustes Generales (Footer)"

    def save(self, *args, **kwargs):
        if not self.pk and PlatformSettings.objects.exists():
            return
        super().save(*args, **kwargs)
