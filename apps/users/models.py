from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Usuario personalizado que soporta roles:
    - CLIENT: Usuario normal que busca citas.
    - EMPLOYEE: Estilista que gestiona su agenda.
    - OWNER: Dueño que crea el negocio.
    """
    ROLE_CHOICES = (
        ('CLIENT', 'Cliente / Usuario'),
        ('EMPLOYEE', 'Colaborador / Estilista'),
        ('OWNER', 'Dueño de Negocio'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CLIENT')
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"