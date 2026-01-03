from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (('CLIENT', 'Cliente'), ('ADMIN', 'Dueño de Negocio'), ('EMPLOYEE', 'Empleado'))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CLIENT')
    phone = models.CharField(max_length=20, blank=True)

# --- NUEVO: Configuración Global del Sitio ---
class PlatformSettings(models.Model):
    whatsapp_number = models.CharField(max_length=50, blank=True, help_text="Número WhatsApp del soporte (ej: 573101234567)")
    instagram_link = models.URLField(blank=True, help_text="Link completo de Instagram (ej: https://instagram.com/paso.app)")
    
    class Meta:
        verbose_name = "Configuración de Plataforma"
        verbose_name_plural = "Configuración de Plataforma"

    def __str__(self):
        return "Ajustes Generales (Footer)"

    def save(self, *args, **kwargs):
        # Evita que se creen múltiples configuraciones
        if not self.pk and PlatformSettings.objects.exists():
            return
        super().save(*args, **kwargs)