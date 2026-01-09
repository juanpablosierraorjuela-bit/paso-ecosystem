from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Superusuario'),
        ('OWNER', 'Dueño de Negocio'),
        ('EMPLOYEE', 'Empleado'),
        ('CLIENT', 'Cliente'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True) # Usaremos dropdown en frontend
    
    # Lógica de Dueño
    is_verified_payment = models.BooleanField(default=False, help_text="¿Pagó los 50k?")
    registration_timestamp = models.DateTimeField(auto_now_add=True)
    
    # Lógica de Empleado
    # 'workplace' es una referencia string para evitar import circular con Businesses
    workplace = models.ForeignKey('businesses.Salon', on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class GlobalSettings(models.Model):
    telegram_token = models.CharField(max_length=255, blank=True, help_text="Token del Bot")
    telegram_chat_id = models.CharField(max_length=255, blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    whatsapp_support = models.CharField(max_length=20, default='573000000000')

    def __str__(self):
        return "Configuración Global del Ecosistema"