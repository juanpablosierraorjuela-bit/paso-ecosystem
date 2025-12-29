from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrador / Dueño"
        MANAGER = "MANAGER", "Gerente"
        EMPLOYEE = "EMPLOYEE", "Empleado / Estilista"
        CUSTOMER = "CUSTOMER", "Cliente"

    role = models.CharField("Rol", max_length=50, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField("Teléfono", max_length=20, blank=True)
    
    # --- NUEVO: VINCULAR EMPLEADO A UN SALÓN ---
    salon = models.ForeignKey('businesses.Salon', on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
