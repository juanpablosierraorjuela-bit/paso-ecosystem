from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('CLIENT', 'Cliente / Usuario'),
        ('EMPLOYEE', 'Colaborador / Estilista'),
        ('OWNER', 'Dueño de Negocio'),
    )
    
    # IMPORTANTE: default='CLIENT' significa que si falla, será cliente.
    # Vamos a asegurarnos en views.py de que no falle.
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CLIENT')
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"