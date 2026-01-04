import os
import subprocess

# RUTA DEL ARCHIVO A CORREGIR
file_path = os.path.join('apps', 'businesses', 'models.py')

# CONTENIDO MEJORADO Y BLINDADO (Timezone Colombia + Lógica Nocturna)
new_content = """from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
import pytz

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salon')
    name = models.CharField(max_length=255, verbose_name="Nombre del Negocio")
    description = models.TextField(verbose_name="Descripción", blank=True)
    city = models.CharField(max_length=100, verbose_name="Ciudad", default="Bogotá")
    address = models.CharField(max_length=255, verbose_name="Dirección Física")
    
    # Redes y Contacto
    whatsapp_number = models.CharField(max_length=50, blank=True)
    instagram_link = models.URLField(blank=True)
    maps_link = models.URLField(blank=True)
    
    # Configuración Financiera
    deposit_percentage = models.IntegerField(default=50)
    
    # Horarios (Formato 24h)
    opening_time = models.TimeField(default="08:00")
    closing_time = models.TimeField(default="20:00")
    
    # Días Laborales
    work_monday = models.BooleanField(default=True)
    work_tuesday = models.BooleanField(default=True)
    work_wednesday = models.BooleanField(default=True)
    work_thursday = models.BooleanField(default=True)
    work_friday = models.BooleanField(default=True)
    work_saturday = models.BooleanField(default=True)
    work_sunday = models.BooleanField(default=False)

    def __str__(self): return self.name

    @property
    def is_open_now(self):
        try:
            # 1. FORZAR HORA COLOMBIA (Siempre)
            bogota_tz = pytz.timezone('America/Bogota')
            now_bogota = timezone.now().astimezone(bogota_tz)
            current_time = now_bogota.time()
            
            # 0=Lunes, 6=Domingo
            today_idx = now_bogota.weekday()
            yesterday_idx = (today_idx - 1) % 7 

            # Mapa de disponibilidad por día
            days_open = {
                0: self.work_monday, 1: self.work_tuesday, 2: self.work_wednesday,
                3: self.work_thursday, 4: self.work_friday, 5: self.work_saturday,
                6: self.work_sunday
            }

            # -----------------------------------------------------------
            # CASO 1: AMANECIDA (El turno de AYER termina HOY en la madrugada)
            # Ej: Sábado 11pm a Domingo 4am. Si es Domingo 2am, debe decir ABIERTO.
            # -----------------------------------------------------------
            # Si ayer se trabajaba Y el horario cruza la medianoche (Abre > Cierra)
            if days_open[yesterday_idx] and self.opening_time > self.closing_time:
                # Si la hora actual es antes del cierre (ej: son las 03:00 y cierra 04:00)
                if current_time < self.closing_time:
                    return True

            # -----------------------------------------------------------
            # CASO 2: TURNO DE HOY
            # -----------------------------------------------------------
            # Si hoy NO se trabaja, devolvemos False (salvo que haya entrado en el Caso 1 arriba)
            if not days_open[today_idx]:
                return False

            # Escenario A: Horario Normal (8:00 a 20:00)
            if self.opening_time <= self.closing_time:
                return self.opening_time <= current_time <= self.closing_time
            
            # Escenario B: Horario Nocturno (23:00 a 04:00) - Parte de "HOY"
            # Aquí solo nos importa si ya abrió (son las 23:30). La parte de la madrugada se evalúa mañana.
            else:
                return current_time >= self.opening_time

        except Exception as e:
            # En caso de error, asumimos cerrado por seguridad, pero imprimimos error en consola
            print(f"Error calculando horario: {e}")
            return False

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField(default=30)
    buffer_time = models.IntegerField(default=10)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class Employee(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='employees')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile', null=True, blank=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    instagram_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class EmployeeSchedule(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='schedule')
    monday_hours = models.CharField(max_length=50, default="09:00-18:00")
    tuesday_hours = models.CharField(max_length=50, default="09:00-18:00")
    wednesday_hours = models.CharField(max_length=50, default="09:00-18:00")
    thursday_hours = models.CharField(max_length=50, default="09:00-18:00")
    friday_hours = models.CharField(max_length=50, default="09:00-18:00")
    saturday_hours = models.CharField(max_length=50, default="09:00-18:00")
    sunday_hours = models.CharField(max_length=50, default="CERRADO")

class Booking(models.Model):
    STATUS_CHOICES = (('PENDING_PAYMENT', 'Pendiente'), ('VERIFIED', 'Confirmada'), ('COMPLETED', 'Completada'), ('CANCELLED', 'Cancelada'))
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    date_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_PAYMENT')
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.end_time and self.service:
            total_min = self.service.duration + self.service.buffer_time
            self.end_time = self.date_time + timedelta(minutes=total_min)
        if not self.deposit_amount and self.salon:
            self.deposit_amount = self.total_price * (self.salon.deposit_percentage / 100)
        super().save(*args, **kwargs)
"""

# 1. ESCRIBIR EL ARCHIVO CON LA NUEVA LÓGICA
print(f"🔄 Actualizando {file_path} con lógica horaria inteligente...")
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("✅ Archivo actualizado correctamente.")

# 2. SUBIR A GITHUB
print("🚀 Subiendo cambios a GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Logic Update: Horario inteligente (Colombia + Nocturno)"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("🎉 Éxito: Código subido a GitHub.")
except Exception as e:
    print(f"⚠️ Alerta Git: {e}")
    print("Intenta hacer 'git push origin master' manualmente si falló.")

# 3. AUTODESTRUCCIÓN
print("💥 Autodestruyendo este script...")
try:
    os.remove(__file__)
    print("👋 Script eliminado. Tu sistema ahora es más inteligente.")
except:
    pass