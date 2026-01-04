from django.db import models

class PlatformSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Paso Ecosystem")
    whatsapp_number = models.CharField(max_length=20, help_text="Ej: 573001234567", blank=True, null=True)
    instagram_link = models.CharField(max_length=200, help_text="URL completa de Instagram", blank=True, null=True)
    footer_text = models.CharField(max_length=200, default="Todos los derechos reservados", blank=True)

    def __str__(self):
        return "Configuración General de la Plataforma"

    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuración del Sistema"
