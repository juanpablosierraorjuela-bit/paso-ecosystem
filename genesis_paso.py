import os
import shutil
import sys

# ==========================================
# CONFIGURACIÓN DEL GÉNESIS
# ==========================================
PROJECT_NAME = "paso_ecosystem"
BASE_DIR = os.getcwd()

# Lista de seguridad: Archivos/Carpetas que NO se borrarán
SAFE_LIST = ['.git', '.venv', 'venv', 'env', 'genesis_paso.py', '__pycache__']

# ==========================================
# 1. EL PURGADOR (BORRA TODO MENOS LO ESENCIAL)
# ==========================================
def purge_directory():
    print("🔥 INICIANDO PURGA DE ARCHIVOS ANTIGUOS...")
    for item in os.listdir(BASE_DIR):
        if item not in SAFE_LIST:
            path = os.path.join(BASE_DIR, item)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                print(f"   🗑️ Eliminado: {item}")
            except Exception as e:
                print(f"   ⚠️ No se pudo eliminar {item}: {e}")
    print("✅ Purga completada. El terreno está limpio.")

# ==========================================
# 2. EL ARQUITECTO (CONTENIDO DE LOS ARCHIVOS)
# ==========================================

# --- REQUIREMENTS.TXT ---
requirements_txt = """
Django>=5.0
gunicorn
psycopg2-binary
whitenoise
django-environ
requests
Pillow
"""

# --- BUILD.SH (Para Render) ---
build_sh = """#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
"""

# --- MANAGE.PY ---
manage_py = """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
"""

# --- CONFIG/SETTINGS.PY ---
settings_py = """
import os
from pathlib import Path
import environ

env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='django-insecure-genesis-key-change-me')
DEBUG = env('DEBUG', default=True)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps del Ecosistema
    'apps.core',
    'apps.businesses',
    'apps.marketplace',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.global_settings', # Footer Dinámico
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}

AUTH_USER_MODEL = 'core.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
"""

# --- APPS/CORE/MODELS.PY (Usuarios y Settings) ---
core_models_py = """
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import requests

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERUSER = "ADMIN", "Arquitecto PASO"
        OWNER = "OWNER", "Dueño de Negocio"
        EMPLOYEE = "EMPLOYEE", "Talento / Empleado"
        CLIENT = "CLIENT", "Cliente Final"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CLIENT)
    phone = models.CharField("WhatsApp", max_length=20, blank=True)
    city = models.CharField("Ciudad", max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Lógica de "El Reaper" (Cobro 24h)
    is_verified_payment = models.BooleanField("Pago Verificado ($50k)", default=False)
    registration_timestamp = models.DateTimeField(auto_now_add=True)
    
    # Vinculación Laboral (Para empleados)
    workplace = models.ForeignKey('businesses.Salon', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')

    def hours_since_registration(self):
        delta = timezone.now() - self.registration_timestamp
        return delta.total_seconds() / 3600

class GlobalSettings(models.Model):
    site_name = models.CharField(max_length=100, default="PASO Ecosistema")
    support_whatsapp = models.CharField(max_length=20, default="573000000000")
    telegram_token = models.CharField(max_length=200, blank=True)
    telegram_chat_id = models.CharField(max_length=100, blank=True)
    instagram_link = models.URLField(blank=True)
    facebook_link = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and GlobalSettings.objects.exists():
            return # Singleton
        super().save(*args, **kwargs)
        
    def send_telegram_test(self):
        if self.telegram_token and self.telegram_chat_id:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {"chat_id": self.telegram_chat_id, "text": "🚀 PASO Ecosistema: Conexión Exitosa"}
            requests.post(url, data=data)
"""

# --- APPS/BUSINESSES/MODELS.PY (Salones, Servicios, Horarios) ---
biz_models_py = """
from django.db import models
from django.conf import settings
from datetime import datetime
import pytz

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salon')
    name = models.CharField("Nombre del Negocio", max_length=255)
    description = models.TextField("Descripción (Buscador Semántico)", blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100) # Dropdown en Frontend
    
    # Redes y Ubicación
    maps_link = models.URLField(blank=True)
    instagram_link = models.URLField(blank=True)
    
    # Configuración de Negocio
    deposit_percentage = models.IntegerField(default=30)
    
    # Horario Global (Overnight Logic)
    opening_time = models.TimeField(default="08:00")
    closing_time = models.TimeField(default="20:00")
    
    # Días de Apertura
    work_monday = models.BooleanField(default=True)
    work_tuesday = models.BooleanField(default=True)
    work_wednesday = models.BooleanField(default=True)
    work_thursday = models.BooleanField(default=True)
    work_friday = models.BooleanField(default=True)
    work_saturday = models.BooleanField(default=True)
    work_sunday = models.BooleanField(default=False)

    def is_open_now(self):
        bogota = pytz.timezone('America/Bogota')
        now = datetime.now(bogota)
        current_time = now.time()
        # Lógica simple, se expandirá en views para overnight
        return True # Simplificado para el ejemplo

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.IntegerField(help_text="Minutos")
    buffer_time = models.IntegerField(default=10, help_text="Minutos de limpieza")
    price = models.DecimalField(max_digits=10, decimal_places=0)
    is_active = models.BooleanField(default=True)

class EmployeeSchedule(models.Model):
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedule')
    # Horarios por día "09:00-18:00" o "CERRADO"
    monday_hours = models.CharField(max_length=50, default="09:00-18:00")
    tuesday_hours = models.CharField(max_length=50, default="09:00-18:00")
    wednesday_hours = models.CharField(max_length=50, default="09:00-18:00")
    thursday_hours = models.CharField(max_length=50, default="09:00-18:00")
    friday_hours = models.CharField(max_length=50, default="09:00-18:00")
    saturday_hours = models.CharField(max_length=50, default="09:00-18:00")
    sunday_hours = models.CharField(max_length=50, default="CERRADO")
"""

# --- APPS/MARKETPLACE/MODELS.PY (Citas y Lógica Booking) ---
market_models_py = """
from django.db import models
from django.conf import settings
from apps.businesses.models import Salon, Service

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente de Abono'), # Cronómetro 60 min
        ('VERIFIED', 'Verificada / Pagada'),
        ('COMPLETED', 'Completada'),
        ('CANCELLED', 'Cancelada'),
    )
    
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='work_appointments')
    
    date_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    total_price = models.DecimalField(max_digits=10, decimal_places=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def minutes_since_creation(self):
        from django.utils import timezone
        delta = timezone.now() - self.created_at
        return delta.total_seconds() / 60
"""

# --- APPS/CORE/MANAGEMENT/COMMANDS/RUN_REAPER.PY (El Ejecutor) ---
reaper_py = """
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import User
from apps.marketplace.models import Appointment
from datetime import timedelta

class Command(BaseCommand):
    help = 'Ejecuta la limpieza automática de usuarios morosos y citas expiradas'

    def handle(self, *args, **kwargs):
        # 1. DUEÑOS MOROSOS (> 24 horas sin verificar pago)
        limit_owners = timezone.now() - timedelta(hours=24)
        owners_to_purge = User.objects.filter(role='OWNER', is_verified_payment=False, registration_timestamp__lt=limit_owners)
        count_owners = owners_to_purge.count()
        owners_to_purge.delete() # O marcar is_active=False para papelera
        
        # 2. CITAS NO ABONADAS (> 60 minutos)
        limit_appointments = timezone.now() - timedelta(minutes=60)
        appointments_to_cancel = Appointment.objects.filter(status='PENDING', created_at__lt=limit_appointments)
        count_apps = appointments_to_cancel.count()
        appointments_to_cancel.update(status='CANCELLED') # O delete()

        self.stdout.write(self.style.SUCCESS(f'Reaper ejecutado: {count_owners} dueños eliminados, {count_apps} citas canceladas.'))
"""

# --- APPS/CORE/CONTEXT_PROCESSORS.PY (Footer Dinámico) ---
context_proc_py = """
from .models import GlobalSettings

def global_settings(request):
    settings = GlobalSettings.objects.first()
    return {'global_settings': settings}
"""

# --- TEMPLATE BASE (Apple Style Minimalista) ---
base_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}PASO Ecosistema{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root { --paso-gold: #d4af37; --paso-black: #111; }
        body { background-color: var(--paso-black); color: white; font-family: 'Helvetica Neue', sans-serif; }
        .btn-paso { background: var(--paso-gold); color: black; border: none; padding: 15px 30px; border-radius: 50px; font-weight: bold; transition: 0.3s; }
        .btn-paso:hover { transform: scale(1.05); background: white; }
        .footer { border-top: 1px solid #333; padding: 20px; margin-top: 50px; font-size: 0.8rem; color: #666; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-black border-bottom border-secondary">
        <div class="container">
            <a class="navbar-brand text-white fw-bold" href="/">PASO</a>
            <div class="d-flex gap-3">
                <a href="/marketplace/" class="text-white text-decoration-none">Marketplace</a>
                {% if user.is_authenticated %}
                    {% if user.role == 'OWNER' %}<a href="/dashboard/" class="btn btn-sm btn-outline-light">Mi Panel</a>{% endif %}
                    {% if user.role == 'EMPLOYEE' %}<a href="/empleado/" class="btn btn-sm btn-outline-light">Mi Agenda</a>{% endif %}
                {% else %}
                    <a href="/login/" class="text-white">Entrar</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>

    <footer class="footer container d-flex justify-content-between align-items-center">
        <div>{{ global_settings.site_name|default:"PASO Ecosistema" }}</div>
        <div>&copy; 2026 Ecosistema PASO</div>
        <div>
            {% if global_settings.instagram_link %}<a href="{{ global_settings.instagram_link }}" class="text-secondary me-2">IG</a>{% endif %}
            {% if global_settings.facebook_link %}<a href="{{ global_settings.facebook_link }}" class="text-secondary">FB</a>{% endif %}
        </div>
    </footer>
</body>
</html>
"""

# --- URLS PRINCIPALES ---
urls_py = """
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('negocio/', include('apps.businesses.urls')),
    path('marketplace/', include('apps.marketplace.urls')),
]
"""

# --- CORE URLS & VIEWS (Placeholder) ---
core_urls_py = """
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro-dueno/', views.register_owner, name='register_owner'),
    path('login/', views.login_view, name='login'),
]
"""
core_views_py = """
from django.shortcuts import render, redirect

def home(request):
    return render(request, 'home.html')
def register_owner(request):
    return render(request, 'registration/register_owner.html') # Placeholder
def login_view(request):
    return render(request, 'registration/login.html') # Placeholder
"""

# --- HOME TEMPLATE ---
home_html = """
{% extends 'base.html' %}
{% block content %}
<div class="text-center" style="padding: 100px 0;">
    <h1 style="font-size: 4rem; font-weight: 700; margin-bottom: 20px;">Ecosistema PASO</h1>
    <p class="text-secondary mb-5" style="font-size: 1.5rem;">Donde la belleza encuentra la inteligencia.</p>
    
    <div class="d-flex justify-content-center gap-4">
        <a href="/marketplace/" class="btn-paso">
            🛍️ Encuentra la Excelencia
            <div style="font-size: 0.8rem; font-weight: normal;">Soy Cliente</div>
        </a>
        <a href="/registro-dueno/" class="btn-paso" style="background: #333; color: white; border: 1px solid #555;">
            💼 Potencia tu Negocio
            <div style="font-size: 0.8rem; font-weight: normal;">Soy Dueño</div>
        </a>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 3. EL CONSTRUCTOR (CREACIÓN DE ARCHIVOS)
# ==========================================
def write_file(path, content):
    full_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"   🔨 Construido: {path}")

def build_structure():
    print("🏗️ LEVANTANDO ESTRUCTURA DE CARPETAS Y ARCHIVOS...")
    
    # 1. Raíz
    write_file('requirements.txt', requirements_txt)
    write_file('build.sh', build_sh)
    write_file('manage.py', manage_py)
    
    # 2. Config
    write_file('config/__init__.py', '')
    write_file('config/settings.py', settings_py)
    write_file('config/urls.py', urls_py)
    write_file('config/wsgi.py', 'import os\nfrom django.core.wsgi import get_wsgi_application\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")\napplication = get_wsgi_application()')
    write_file('config/asgi.py', 'import os\nfrom django.core.asgi import get_asgi_application\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")\napplication = get_asgi_application()')

    # 3. Apps (Core, Businesses, Marketplace)
    for app in ['core', 'businesses', 'marketplace']:
        write_file(f'apps/{app}/__init__.py', '')
        write_file(f'apps/{app}/admin.py', 'from django.contrib import admin\n# Register your models here.')
        write_file(f'apps/{app}/apps.py', f'from django.apps import AppConfig\nclass {app.capitalize()}Config(AppConfig):\n    default_auto_field = "django.db.models.BigAutoField"\n    name = "apps.{app}"')
        write_file(f'apps/{app}/tests.py', '')
        write_file(f'apps/{app}/urls.py', 'from django.urls import path\nfrom . import views\nurlpatterns = []')
        write_file(f'apps/{app}/views.py', 'from django.shortcuts import render\n# Views here')

    # Modelos Específicos
    write_file('apps/core/models.py', core_models_py)
    write_file('apps/core/context_processors.py', context_proc_py)
    write_file('apps/core/urls.py', core_urls_py)
    write_file('apps/core/views.py', core_views_py)
    write_file('apps/core/management/commands/run_reaper.py', reaper_py)
    write_file('apps/core/management/commands/__init__.py', '')

    write_file('apps/businesses/models.py', biz_models_py)
    write_file('apps/marketplace/models.py', market_models_py)

    # 4. Templates
    write_file('templates/base.html', base_html)
    write_file('templates/home.html', home_html)
    write_file('templates/registration/login.html', '<h1>Login Placeholder</h1>')
    write_file('templates/registration/register_owner.html', '<h1>Registro Dueño Placeholder</h1>')
    
    # Static
    os.makedirs(os.path.join(BASE_DIR, 'static/css'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'static/js'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'static/img'), exist_ok=True)

    print("✨ Estructura completada.")

# ==========================================
# EJECUCIÓN MAESTRA
# ==========================================
if __name__ == "__main__":
    print(f"🚀 INICIANDO GÉNESIS DE {PROJECT_NAME}")
    
    confirm = input("⚠️  ESTO BORRARÁ TODO EXCEPTO .git ¿ESTÁS SEGURO? (escribe 'si' para continuar): ")
    if confirm.lower() == 'si':
        purge_directory()
        build_structure()
        
        # Permisos de ejecución para build.sh
        if os.name != 'nt': # Solo en Linux/Mac
            os.system('chmod +x build.sh')
            
        print("\n✅ ¡GÉNESIS COMPLETADO!")
        print("👉 PASOS SIGUIENTES OBLIGATORIOS:")
        print("   1. Instala dependencias: pip install -r requirements.txt")
        print("   2. Crea la base de datos: python manage.py makemigrations core businesses marketplace")
        print("   3. Aplica cambios: python manage.py migrate")
        print("   4. Crea tu Superusuario (TÚ): python manage.py createsuperuser")
        print("   5. Sube a GitHub: git add . && git commit -m 'Genesis: New Beginning' && git push origin main")
    else:
        print("❌ Operación cancelada.")