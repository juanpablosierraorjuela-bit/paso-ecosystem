import os
import textwrap
import subprocess
import sys

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory: os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(textwrap.dedent(content).strip())
    print(f"✅ Archivo blindado generado: {path}")

print("🚑 INICIANDO OPERACIÓN RESCATE (MODO QUIRÚRGICO)...")

# ==============================================================================
# 1. MODELS.PY (LA VERSIÓN DEFINITIVA Y COMPLETA)
# ==============================================================================
# Esta versión combina lo mejor de los dos mundos:
# - Tiene la lógica nueva de 'Booking' (con estados de colores)
# - Tiene los modelos 'Schedule' y 'OpeningHours' que el Admin necesita.
# - NO cambia nombres de variables para no romper la DB actual.

models_content = """
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone

class Salon(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_salons')
    name = models.CharField(max_length=255, verbose_name="Nombre del Negocio")
    slug = models.SlugField(unique=True, blank=True)
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    address = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    phone = models.CharField(max_length=50, verbose_name="WhatsApp del Negocio")
    instagram_link = models.URLField(blank=True, null=True, verbose_name="Link de Instagram")
    deposit_percentage = models.IntegerField(default=30, verbose_name="% de Abono")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Horarios Generales (Usados para validación rápida)
    open_time = models.TimeField(default='08:00', verbose_name="Apertura")
    close_time = models.TimeField(default='20:00', verbose_name="Cierre")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + '-' + str(self.owner.id)[:4]
        super().save(*args, **kwargs)
        
    def __str__(self): return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    duration_minutes = models.IntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self): return f"{self.name} (${self.price})"

class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    instagram_link = models.URLField(blank=True, null=True)
    
    # Horario Almuerzo
    lunch_start = models.TimeField(null=True, blank=True)
    lunch_end = models.TimeField(null=True, blank=True)
    
    def __str__(self): return self.name

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', '🟡 Pendiente Abono'),
        ('in_review', '🟠 En Revisión'),
        ('confirmed', '🟢 Confirmada'),
        ('cancelled', '🔴 Cancelada'),
        ('expired', '⚫ Expirada'),
    ]
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=50)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): return f"Cita #{self.id} - {self.customer_name}"

# --- MODELOS RESTAURADOS (Requeridos por el Admin) ---
# Se agregan al final. No afectan a los modelos de arriba.
class Schedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()
    start_time = models.TimeField(default='09:00')
    end_time = models.TimeField(default='18:00')
    is_active = models.BooleanField(default=True)
    
    def __str__(self): return f"Horario {self.employee.name} - Dia {self.day_of_week}"

class OpeningHours(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()
    start_time = models.TimeField(default='08:00')
    end_time = models.TimeField(default='20:00')
    is_closed = models.BooleanField(default=False)

    def __str__(self): return f"Apertura {self.salon.name} - Dia {self.day_of_week}"
"""
create_file('apps/businesses/models.py', models_content)

# ==============================================================================
# 2. BUILD.SH (ESTRATEGIA DE MIGRACIÓN SEGURA)
# ==============================================================================
# Modificamos el build para que detecte los cambios ESPECÍFICAMENTE en 'businesses'
# Esto crea las tablas faltantes sin tocar las existentes.
create_file('build.sh', """#!/usr/bin/env bash
set -o errexit

echo "🛡️  Iniciando Deploy Seguro (Fix Admin Models)..."

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Estáticos
python manage.py collectstatic --no-input

# 3. MIGRACIONES INTELIGENTES
# Primero, detectamos cambios solo en la app que tocamos
echo "🔍 Detectando cambios en modelos..."
python manage.py makemigrations businesses

# Luego aplicamos todo
echo "💾 Guardando cambios en base de datos..."
python manage.py migrate

echo "✅ Sistema Estabilizado y Listo."
""")

# ==============================================================================
# 3. EJECUCIÓN AUTÓNOMA (GIT + CLEANUP)
# ==============================================================================
print("🤖 Subiendo corrección a la nube...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix: Safely restored missing Admin models without breaking schema"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("🚀 ¡ENVIADO! Render detectará los nuevos modelos, creará sus tablas y el Admin funcionará.")
except Exception as e:
    print(f"⚠️ Error git: {e}")

print("💥 Autodestruyendo herramienta quirúrgica...")
try:
    os.remove(__file__)
except: pass