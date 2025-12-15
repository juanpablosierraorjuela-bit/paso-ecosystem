from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser): # Asegúrate que tu proyecto usa 'User' o 'CustomUser'
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrador / Dueño"
        MANAGER = "MANAGER", "Gerente / Recepción"
        EMPLOYEE = "EMPLOYEE", "Empleado / Estilista"
        INDEPENDENT = "INDEPENDENT", "Domiciliario / Externo"
        CUSTOMER = "CUSTOMER", "Cliente Final"

    role = models.CharField("Rol", max_length=50, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField("Teléfono / WhatsApp", max_length=20, blank=True)
    identification = models.CharField("Cédula / NIT", max_length=20, blank=True)
    address = models.CharField("Dirección", max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)