import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
MODELS_PATH = os.path.join(APP_DIR, "models.py")

# --- CONTENIDO COMPLETO Y CORREGIDO DE MODELS.PY ---
CONTENIDO_MODELOS = """from django.db import models
from django.conf import settings

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salon')
    name = models.CharField(max_length=255, verbose_name="Nombre del Negocio")
    description = models.TextField(verbose_name="Descripción", blank=True)
    address = models.CharField(max_length=255, verbose_name="Dirección Física")
    city = models.CharField(max_length=100, default='Bogotá', verbose_name="Ciudad")
    phone = models.CharField(max_length=50, verbose_name="Teléfono", blank=True, default='')
    email = models.EmailField(verbose_name="Correo del Negocio", blank=True)
    whatsapp = models.CharField(max_length=50, blank=True, verbose_name="WhatsApp")
    instagram = models.CharField(max_length=100, blank=True, verbose_name="Instagram")

    def __str__(self):
        return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100, verbose_name="Nombre del Servicio")
    description = models.TextField(blank=True, verbose_name="Descripción")
    duration_minutes = models.IntegerField(default=30, verbose_name="Duración (min)")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Precio")

    def __str__(self):
        return self.name

class Employee(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='employees')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile', null=True, blank=True)
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellido")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# --- ESTE ERA EL QUE FALTABA ---
class SalonSchedule(models.Model):
    salon = models.OneToOneField(Salon, on_delete=models.CASCADE, related_name='schedule')
    monday_open = models.BooleanField(default=True, verbose_name="Lunes")
    tuesday_open = models.BooleanField(default=True, verbose_name="Martes")
    wednesday_open = models.BooleanField(default=True, verbose_name="Miércoles")
    thursday_open = models.BooleanField(default=True, verbose_name="Jueves")
    friday_open = models.BooleanField(default=True, verbose_name="Viernes")
    saturday_open = models.BooleanField(default=True, verbose_name="Sábado")
    sunday_open = models.BooleanField(default=False, verbose_name="Domingo")

    def __str__(self):
        return f"Horario de {self.salon.name}"

class EmployeeSchedule(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='schedule')
    monday_hours = models.CharField(max_length=50, default="09:00-18:00", blank=True)
    tuesday_hours = models.CharField(max_length=50, default="09:00-18:00", blank=True)
    wednesday_hours = models.CharField(max_length=50, default="09:00-18:00", blank=True)
    thursday_hours = models.CharField(max_length=50, default="09:00-18:00", blank=True)
    friday_hours = models.CharField(max_length=50, default="09:00-18:00", blank=True)
    saturday_hours = models.CharField(max_length=50, default="09:00-18:00", blank=True)
    sunday_hours = models.CharField(max_length=50, default="CERRADO", blank=True)

    def __str__(self):
        return f"Horario de {self.employee}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente de Abono'),
        ('confirmed', 'Cita Verificada'),
        ('cancelled', 'Cancelada'),
    ]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='bookings')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='bookings')
    services = models.ManyToManyField(Service)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} - {self.date} {self.time}"
"""

def restaurar_modelos():
    print("🚑 Restaurando models.py completo...")
    with open(MODELS_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_MODELOS)
    print("✅ Archivo models.py reparado exitosamente.")

if __name__ == "__main__":
    restaurar_modelos()