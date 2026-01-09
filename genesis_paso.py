import os
import shutil
import sys
from pathlib import Path

# ==========================================
# CONFIGURACIÓN DEL GÉNESIS
# ==========================================
PROJECT_NAME = "config"  # Nombre de la carpeta de configuración Django
BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. EL DESTRUCTOR (LIMPIEZA)
# ==========================================
def clean_directory():
    print("🔥 INICIANDO PROTOCOLO DE LIMPIEZA...")
    for item in os.listdir(BASE_DIR):
        if item.startswith(".git") or item == os.path.basename(__file__):
            continue
        
        item_path = BASE_DIR / item
        try:
            if item_path.is_dir():
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
            print(f"   - Eliminado: {item}")
        except Exception as e:
            print(f"   ⚠️ Error eliminando {item}: {e}")
    print("✅ LIMPIEZA COMPLETADA. El terreno está listo.")

# ==========================================
# 2. LOS PLANOS (CONTENIDO DE ARCHIVOS)
# ==========================================

files_content = {}

# --- MANAGE.PY ---
files_content["manage.py"] = """#!/usr/bin/env python
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

# --- REQUIREMENTS.TXT ---
files_content["requirements.txt"] = """
Django>=5.0
Pillow
requests
"""

# --- CONFIG / SETTINGS.PY ---
files_content["config/settings.py"] = """
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-genesis-key-change-me-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # APPS DEL ECOSISTEMA PASO
    'apps.core',
    'apps.businesses',
    'apps.marketplace',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Context Processor para el Footer Dinámico
                'apps.core.context_processors.global_settings', 
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- MODELO DE USUARIO PERSONALIZADO ---
AUTH_USER_MODEL = 'core.User'

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
"""

# --- CONFIG / URLS.PY ---
files_content["config/urls.py"] = """
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Rutas Principales (La Constitución)
    path('', include('apps.core.urls')),
    path('negocio/', include('apps.businesses.urls')),
    path('marketplace/', include('apps.marketplace.urls')),
]
"""

# --- APPS / CORE / MODELS.PY ---
files_content["apps/core/models.py"] = """
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
"""

# --- APPS / CORE / ADMIN.PY ---
files_content["apps/core/admin.py"] = """
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, GlobalSettings

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'role', 'email', 'is_verified_payment', 'date_joined')
    list_filter = ('role', 'is_verified_payment')
    fieldsets = UserAdmin.fieldsets + (
        ('Datos PASO', {'fields': ('role', 'phone', 'city', 'is_verified_payment', 'workplace')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(GlobalSettings)
"""

# --- APPS / CORE / VIEWS.PY ---
files_content["apps/core/views.py"] = """
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import OwnerRegistrationForm # Se creará luego

def home(request):
    return render(request, 'home.html')

def register_owner(request):
    if request.method == 'POST':
        # Aquí irá la lógica de registro y guardado de timestamp
        pass
    return render(request, 'registration/register_owner.html')

def login_view(request):
    return render(request, 'registration/login.html')
"""

# --- APPS / CORE / URLS.PY ---
files_content["apps/core/urls.py"] = """
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro-dueno/', views.register_owner, name='register_owner'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
"""

# --- APPS / CORE / CONTEXT_PROCESSORS.PY ---
files_content["apps/core/context_processors.py"] = """
from .models import GlobalSettings

def global_settings(request):
    settings = GlobalSettings.objects.first()
    return {'global_settings': settings}
"""

# --- APPS / CORE / MANAGEMENT / COMMANDS / RUN_REAPER.PY ---
files_content["apps/core/management/commands/run_reaper.py"] = """
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import User
from datetime import timedelta

class Command(BaseCommand):
    help = 'El Reaper: Elimina cuentas no pagadas > 24h y citas pendientes > 60min'

    def handle(self, *args, **kwargs):
        # 1. Eliminar Dueños Morosos
        limit_time = timezone.now() - timedelta(hours=24)
        expired_owners = User.objects.filter(role='OWNER', is_verified_payment=False, registration_timestamp__lt=limit_time)
        count = expired_owners.count()
        expired_owners.delete() # O usar is_active = False como sugeriste
        self.stdout.write(self.style.SUCCESS(f'Reaper: {count} cuentas eliminadas.'))
        
        # 2. Aquí iría la lógica para eliminar citas pendientes (cuando creemos el modelo Appointment)
"""

# --- APPS / BUSINESSES / MODELS.PY ---
files_content["apps/businesses/models.py"] = """
from django.db import models
from django.conf import settings

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_salon')
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Configuración de Horario del Negocio
    opening_time = models.TimeField()
    closing_time = models.TimeField() # Maneja lógica nocturna si close < open
    
    deposit_percentage = models.IntegerField(default=50, help_text="Porcentaje de abono requerido")
    
    # Redes para el Marketplace
    instagram_url = models.URLField(blank=True)
    google_maps_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    duration_minutes = models.IntegerField(help_text="Duración en minutos")
    buffer_time = models.IntegerField(default=15, help_text="Tiempo de limpieza post-servicio")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} - {self.salon.name}"

class EmployeeSchedule(models.Model):
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedule')
    # Aquí irían los JSON o campos para los horarios por día (Lunes a Domingo)
    # Por simplicidad inicial, dejamos el placeholder
    is_active_today = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Horario de {self.employee.username}"
"""

# --- APPS / BUSINESSES / URLS.PY ---
files_content["apps/businesses/urls.py"] = """
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.owner_dashboard, name='dashboard'),
    # path('mi-agenda/', views.employee_dashboard, name='employee_dashboard'),
]
"""

# --- APPS / BUSINESSES / VIEWS.PY ---
files_content["apps/businesses/views.py"] = """
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def owner_dashboard(request):
    # Lógica del temporizador y validación
    return render(request, 'businesses/dashboard.html')
"""

# --- APPS / MARKETPLACE / MODELS.PY ---
files_content["apps/marketplace/models.py"] = """
from django.db import models
from django.conf import settings

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente de Abono'),
        ('VERIFIED', 'Verificada'),
        ('COMPLETED', 'Completada'),
        ('CANCELLED', 'Cancelada'),
    )
    
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    salon = models.ForeignKey('businesses.Salon', on_delete=models.CASCADE)
    service = models.ForeignKey('businesses.Service', on_delete=models.CASCADE)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='work_appointments')
    
    date_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Cita {self.id} - {self.client.username}"
"""

# --- APPS / MARKETPLACE / URLS.PY ---
files_content["apps/marketplace/urls.py"] = """
from django.urls import path
# from . import views

urlpatterns = [
    # path('', views.home, name='marketplace_home'),
]
"""

# --- TEMPLATES / BASE.HTML ---
files_content["templates/base.html"] = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PASO Ecosistema</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@300;400&display=swap');
        .font-serif { family: 'Playfair Display', serif; }
        .font-sans { family: 'Lato', sans-serif; }
    </style>
</head>
<body class="bg-gray-50 font-sans flex flex-col min-h-screen">

    <main class="flex-grow">
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-black text-white py-6 mt-12">
        <div class="container mx-auto px-4 flex justify-between items-center">
            <div class="text-sm font-bold tracking-widest text-gold-500">
                PASO ECOSISTEMA
            </div>
            
            <div class="text-xs text-gray-400">
                &copy; 2026 - Ecosistema PASO
            </div>
            
            <div class="flex space-x-4">
                {% if global_settings.instagram_url %}
                    <a href="{{ global_settings.instagram_url }}" class="hover:text-pink-500">IG</a>
                {% endif %}
                {% if global_settings.whatsapp_support %}
                    <a href="https://wa.me/{{ global_settings.whatsapp_support }}" class="hover:text-green-500">WA</a>
                {% endif %}
            </div>
        </div>
    </footer>

</body>
</html>
"""

# --- TEMPLATES / HOME.HTML ---
files_content["templates/home.html"] = """
{% extends 'base.html' %}

{% block content %}
<div class="h-screen flex items-center justify-center bg-white">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-12 max-w-4xl w-full p-8">
        
        <a href="/marketplace/" class="group block text-center p-12 border border-gray-100 rounded-3xl shadow-xl hover:shadow-2xl transition-all hover:scale-105 bg-white">
            <div class="text-6xl mb-6">🔍</div>
            <h2 class="text-3xl font-serif text-gray-900 mb-2">Clientes</h2>
            <p class="text-gray-500">Encuentra la Excelencia</p>
        </a>

        <a href="{% url 'register_owner' %}" class="group block text-center p-12 border border-gray-900 bg-black text-white rounded-3xl shadow-xl hover:shadow-2xl transition-all hover:scale-105">
            <div class="text-6xl mb-6">🚀</div>
            <h2 class="text-3xl font-serif text-white mb-2">Dueños</h2>
            <p class="text-gray-400">Potencia tu Ecosistema</p>
        </a>
        
    </div>
</div>
{% endblock %}
"""

# --- TEMPLATES / REGISTRATION / REGISTER_OWNER.HTML ---
files_content["templates/registration/register_owner.html"] = """
{% extends 'base.html' %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-lg">
        <div>
            <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 font-serif">
                Bienvenido al Club
            </h2>
            <p class="mt-2 text-center text-sm text-gray-600">
                Únete a la élite de la belleza en Colombia.
            </p>
        </div>
        <form class="mt-8 space-y-6" action="#" method="POST">
            {% csrf_token %}
            <div class="rounded-md shadow-sm -space-y-px">
                <p class="text-center text-gray-400">Formulario Inteligente de Registro (Placeholder)</p>
            </div>

            <div>
                <button type="submit" class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-black hover:bg-gray-800 focus:outline-none transition-colors">
                    Registrar mi Ecosistema
                </button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
"""

# --- TEMPLATES / BUSINESSES / DASHBOARD.HTML ---
files_content["templates/businesses/dashboard.html"] = """
{% extends 'base.html' %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8">
        <div class="flex">
            <div class="flex-shrink-0">
                ⚠️
            </div>
            <div class="ml-3">
                <p class="text-sm text-yellow-700">
                    <span class="font-bold">Acción Requerida:</span>
                    Tu cuenta está en periodo de prueba. Tienes <span id="timer" class="font-mono font-bold">23:59:00</span> para activar tu ecosistema.
                </p>
                <a href="#" class="mt-2 inline-block text-sm font-bold text-yellow-800 underline">Pagar $50.000 COP y Activar</a>
            </div>
        </div>
    </div>

    <h1 class="text-4xl font-serif mb-6">Panel de Control: El Cerebro</h1>
    </div>
{% endblock %}
"""


# ==========================================
# 3. EL CONSTRUCTOR (CREACIÓN DE ARCHIVOS)
# ==========================================
def build_structure():
    print("🏗️  LEVANTANDO EL ECOSISTEMA PASO...")
    
    # 1. Crear carpetas de Apps
    apps = ['core', 'businesses', 'marketplace']
    for app in apps:
        app_path = BASE_DIR / 'apps' / app
        management_path = app_path / 'management' / 'commands'
        migrations_path = app_path / 'migrations'
        
        os.makedirs(app_path, exist_ok=True)
        os.makedirs(management_path, exist_ok=True)
        os.makedirs(migrations_path, exist_ok=True)
        
        # Crear __init__.py en cada nivel
        Path(app_path / '__init__.py').touch()
        Path(BASE_DIR / 'apps' / '__init__.py').touch()
        Path(management_path / '__init__.py').touch()
        Path(management_path.parent / '__init__.py').touch()
        Path(migrations_path / '__init__.py').touch()

    # 2. Crear carpetas de Configuración
    os.makedirs(BASE_DIR / PROJECT_NAME, exist_ok=True)
    Path(BASE_DIR / PROJECT_NAME / '__init__.py').touch()
    
    # 3. Crear carpetas de Templates
    os.makedirs(BASE_DIR / 'templates' / 'registration', exist_ok=True)
    os.makedirs(BASE_DIR / 'templates' / 'businesses', exist_ok=True)
    os.makedirs(BASE_DIR / 'templates' / 'marketplace', exist_ok=True)
    
    # 4. Crear carpetas Static
    os.makedirs(BASE_DIR / 'static' / 'css', exist_ok=True)
    os.makedirs(BASE_DIR / 'static' / 'js', exist_ok=True)
    os.makedirs(BASE_DIR / 'static' / 'img', exist_ok=True)

    # 5. Escribir Archivos
    for filename, content in files_content.items():
        file_path = BASE_DIR / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"   + Creado: {filename}")

    # 6. Crear archivos extra necesarios (wsgi/asgi)
    with open(BASE_DIR / 'config' / 'wsgi.py', 'w') as f:
        f.write("import os\nfrom django.core.wsgi import get_wsgi_application\nos.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')\napplication = get_wsgi_application()")
    
    with open(BASE_DIR / 'config' / 'asgi.py', 'w') as f:
        f.write("import os\nfrom django.core.asgi import get_asgi_application\nos.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')\napplication = get_asgi_application()")

    print("\n✅ CONSTRUCCIÓN FINALIZADA.")
    print("==================================================")
    print("🚀 PASOS SIGUIENTES PARA DAR VIDA AL UNICORNIO:")
    print("1. Activa tu entorno virtual (si no lo has hecho).")
    print("2. Instala dependencias: pip install -r requirements.txt")
    print("3. Crea la base de datos: python manage.py migrate")
    print("4. Crea tu Superusuario (Arquitecto): python manage.py createsuperuser")
    print("5. Corre el servidor: python manage.py runserver")
    print("==================================================")

if __name__ == "__main__":
    clean_directory()
    build_structure()