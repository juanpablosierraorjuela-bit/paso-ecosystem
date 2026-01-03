from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (('CLIENT', 'Cliente'), ('ADMIN', 'Dueño de Negocio'), ('EMPLOYEE', 'Empleado'))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CLIENT')
    phone = models.CharField(max_length=20, blank=True)