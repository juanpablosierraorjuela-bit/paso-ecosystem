import os
import sys
import textwrap

def create_file(path, content):
    # FIX WINDOWS: Solo crea carpeta si la ruta tiene una carpeta padre
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
        
    # Escribe el archivo con codificación UTF-8
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(textwrap.dedent(content).strip())
    print(f"✅ Creado: {path}")

print("🚀 INICIANDO GÉNESIS DEL SISTEMA (Versión Windows Corregida)...")

# ==============================================================================
# 1. RAIZ DEL PROYECTO (Archivos de gestión)
# ==============================================================================

# requirements.txt
create_file('requirements.txt', """
Django==5.0.3
djangorestframework==3.15.1
psycopg2-binary==2.9.9
gunicorn==21.2.0
dj-database-url==2.1.0
whitenoise==6.6.0
django-cors-headers==4.3.1
""")

# build.sh
create_file('build.sh', """#!/usr/bin/env bash
set -o errexit

echo "🏗️ Construyendo Proyecto..."
pip install -r requirements.txt

echo "🎨 Recopilando Estáticos..."
python manage.py collectstatic --no-input

echo "🔧 Migraciones..."
# Forzamos creación de tablas nuevas
python manage.py makemigrations core_saas
python manage.py makemigrations businesses
python manage.py makemigrations
python manage.py migrate

echo "✅ Listo para despegar."
""")

# manage.py
create_file('manage.py', """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paso_ecosystem.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
""")

# ==============================================================================
# 2. CONFIGURACIÓN (Carpeta 'paso_ecosystem')
# ==============================================================================

# paso_ecosystem/settings.py
create_file('paso_ecosystem/settings.py', """
from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-genesis-key-2026')
DEBUG = 'RENDER' not in os.environ
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Librerías
    'django.contrib.humanize',
    'rest_framework',
    'corsheaders',
    
    # Tus Apps
    'apps.core_saas',
    'apps.businesses',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'paso_ecosystem.urls'

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
                'apps.businesses.context_processors.owner_check',
            ],
        },
    },
]

WSGI_APPLICATION = 'paso_ecosystem.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

AUTH_PASSWORD_VALIDATORS = [] # Sin validaciones estrictas por ahora

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

AUTH_USER_MODEL = 'core_saas.User'
LOGIN_URL = 'saas_login'
LOGIN_REDIRECT_URL = 'client_dashboard'
LOGOUT_REDIRECT_URL = 'home'
""")

# paso_ecosystem/urls.py
create_file('paso_ecosystem/urls.py', """
from django.contrib import admin
from django.urls import path, include
from apps.businesses import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('negocio/<slug:slug>/', views.salon_detail, name='salon_detail'),
    
    # Flujo Reserva
    path('reserva/iniciar/', views.booking_wizard_start, name='booking_wizard_start'),
    path('reserva/profesional/', views.booking_step_employee, name='booking_step_employee'),
    path('reserva/fecha/', views.booking_step_datetime, name='booking_step_datetime'),
    path('reserva/contacto/', views.booking_step_contact, name='booking_step_contact'),
    path('reserva/crear/', views.booking_create, name='booking_create'),
    
    # Paneles
    path('mi-panel/', views.client_dashboard, name='client_dashboard'),
    path('negocio-panel/', views.owner_dashboard, name='owner_dashboard'),
    path('confirmar-pago/<int:booking_id>/', views.booking_confirm_payment, name='booking_confirm_payment'),
    
    # Auth
    path('login/', views.saas_login, name='saas_login'),
    path('logout/', views.saas_logout, name='saas_logout'),
    path('registro-negocio/', views.register_owner, name='register_owner'),
]
""")

# paso_ecosystem/wsgi.py
create_file('paso_ecosystem/wsgi.py', """
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paso_ecosystem.settings')
application = get_wsgi_application()
""")

# paso_ecosystem/__init__.py
create_file('paso_ecosystem/__init__.py', "")

# ==============================================================================
# 3. APLICACIONES (apps)
# ==============================================================================

# --- APP: core_saas (Usuarios) ---
create_file('apps/core_saas/__init__.py', "")
create_file('apps/core_saas/apps.py', "from django.apps import AppConfig\nclass CoreSaasConfig(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = 'apps.core_saas'")

create_file('apps/core_saas/models.py', """
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (('CLIENT', 'Cliente'), ('ADMIN', 'Dueño de Negocio'), ('EMPLOYEE', 'Empleado'))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CLIENT')
    phone = models.CharField(max_length=20, blank=True)
""")

# --- APP: businesses (Lógica) ---
create_file('apps/businesses/__init__.py', "")
create_file('apps/businesses/apps.py', "from django.apps import AppConfig\nclass BusinessesConfig(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = 'apps.businesses'")

create_file('apps/businesses/models.py', """
from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Salon(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    instagram_link = models.URLField(blank=True, null=True)
    deposit_percentage = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name) + '-' + str(self.owner.id)[:4]
        super().save(*args, **kwargs)

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    duration_minutes = models.IntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

class Schedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()
    start_time = models.TimeField(default='09:00')
    end_time = models.TimeField(default='18:00')
    is_active = models.BooleanField(default=True)
    lunch_start = models.TimeField(null=True, blank=True)
    lunch_end = models.TimeField(null=True, blank=True)

class OpeningHours(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()
    start_time = models.TimeField(default='08:00')
    end_time = models.TimeField(default='20:00')
    is_closed = models.BooleanField(default=False)

class Booking(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=50)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, default='pending_payment')
    created_at = models.DateTimeField(auto_now_add=True)
""")

create_file('apps/businesses/views.py', """
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
import urllib.parse
from .forms import *
from .models import Salon, Service, Booking, Employee, Schedule, OpeningHours

User = get_user_model()

def get_salon(user): return Salon.objects.filter(owner=user).first()

def check_expired_bookings():
    try:
        limit = timezone.now() - timedelta(minutes=30)
        Booking.objects.filter(status='pending_payment', created_at__lt=limit).update(status='expired')
    except: pass

def get_available_slots(employee, check_date, duration=60):
    check_expired_bookings()
    day_idx = check_date.weekday()
    # Lógica simplificada de horarios (asumiendo que existen)
    try:
        sched = Schedule.objects.filter(employee=employee, day_of_week=day_idx, is_active=True).first()
        if not sched: return []
        slots = []
        current = datetime.combine(check_date, sched.start_time)
        limit = datetime.combine(check_date, sched.end_time)
        
        # Filtro hoy
        if check_date == date.today():
            if current < datetime.now() + timedelta(minutes=30):
                current = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        while current + timedelta(minutes=duration) <= limit:
            # Aquí iría el check de colisiones real
            slots.append(current.strftime('%H:%M'))
            current += timedelta(minutes=30)
        return slots
    except: return []

# WIZARD
def booking_wizard_start(request): 
    sid = request.POST.getlist('service_ids')
    if not sid: return redirect('home')
    request.session['booking']={'salon_slug':request.POST.get('salon_slug'), 'service_ids':sid}
    return redirect('booking_step_employee')

def booking_step_employee(request):
    d = request.session.get('booking')
    s = get_object_or_404(Salon, slug=d['salon_slug'])
    if request.method == 'POST':
        request.session['booking']['emp_id'] = request.POST.get('employee_id')
        request.session.modified = True
        return redirect('booking_step_datetime')
    return render(request, 'booking_wizard_employee.html', {'salon': s, 'employees': Employee.objects.filter(salon=s)})

def booking_step_datetime(request):
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    date_str = request.GET.get('date', date.today().isoformat())
    return render(request, 'booking_wizard_datetime.html', {'salon': s, 'slots': ['09:00', '10:00', '11:00'], 'selected_date': date_str})

def booking_step_contact(request):
    if request.method == 'POST':
        request.session['booking'].update({'date': request.POST.get('date'), 'time': request.POST.get('time')})
        request.session.modified = True
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    total = sum(sv.price for sv in Service.objects.filter(id__in=d['service_ids']))
    porcentaje = Decimal(s.deposit_percentage) / Decimal(100)
    return render(request, 'booking_contact.html', {'salon': s, 'total': total, 'abono': total * porcentaje, 'porcentaje': s.deposit_percentage})

def booking_create(request):
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    email = request.POST['customer_email']
    u, created = User.objects.get_or_create(email=email, defaults={'username': email})
    if created: u.set_password('123456'); u.save()
    login(request, u, backend='django.contrib.auth.backends.ModelBackend')
    
    emp = Employee.objects.filter(salon=s).first() # Fallback simple
    for sid in d['service_ids']:
        Booking.objects.create(salon=s, service_id=sid, employee=emp, customer_name=request.POST['customer_name'], customer_email=email, customer_phone=request.POST['customer_phone'], date=d['date'], time=d['time'])
    
    del request.session['booking']
    return redirect('client_dashboard')

# DASHBOARDS
@login_required
def client_dashboard(request):
    check_expired_bookings()
    bookings = Booking.objects.filter(customer_email=request.user.email)
    citas = []
    for b in bookings:
        precio = b.service.price
        porcentaje = Decimal(b.salon.deposit_percentage) / Decimal(100)
        abono = precio * porcentaje
        msg = f"Hola {b.salon.name}, pago cita #{b.id}. Abono: ${abono:,.0f}."
        citas.append({'obj': b, 'abono': abono, 'pendiente': precio - abono, 'wa_link': f"https://wa.me/{b.salon.phone}?text={urllib.parse.quote(msg)}"})
    return render(request, 'client_dashboard.html', {'citas': citas})

@login_required
def owner_dashboard(request):
    return render(request, 'dashboard/owner_dashboard.html', {'salon': get_salon(request.user)})

@login_required
def booking_confirm_payment(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id)
    b.status = 'confirmed'; b.save()
    return redirect('owner_dashboard')

# AUTH
def saas_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid(): login(request, form.get_user()); return redirect('client_dashboard')
    return render(request, 'registration/login.html', {'form': UserLoginForm()})

def register_owner(request):
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            u = User.objects.create_user(username=form.cleaned_data['email'], email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            Salon.objects.create(owner=u, name=form.cleaned_data['nombre_negocio'], city=form.cleaned_data['ciudad'], phone=form.cleaned_data['whatsapp'])
            login(request, u, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('owner_dashboard')
    return render(request, 'registration/register_owner.html', {'form': OwnerRegistrationForm()})

def home(request): return render(request, 'home.html')
def marketplace(request): return render(request, 'marketplace.html', {'salons': Salon.objects.all()})
def salon_detail(request, slug): 
    s = get_object_or_404(Salon, slug=slug)
    return render(request, 'salon_detail.html', {'salon': s, 'services': Service.objects.filter(salon=s)})
def saas_logout(request): logout(request); return redirect('home')
""")

create_file('apps/businesses/forms.py', """
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))

class OwnerRegistrationForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    nombre_negocio = forms.CharField()
    ciudad = forms.CharField()
    whatsapp = forms.CharField()
    instagram = forms.CharField(required=False)
""")

create_file('apps/businesses/context_processors.py', """
from .models import Salon
def owner_check(request):
    try:
        if request.user.is_authenticated:
            salon = Salon.objects.filter(owner=request.user).first()
            return {'is_owner': bool(salon), 'user_salon': salon}
    except: pass
    return {'is_owner': False}
""")

# ==============================================================================
# 4. TEMPLATES (Base y Diseño)
# ==============================================================================

create_file('templates/base.html', """
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paso Marketplace</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f8f9fa; }
        .navbar-brand { font-weight: 800; color: #667eea !important; }
        .btn-gradient { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
        <div class="container">
            <a class="navbar-brand" href="{% url 'home' %}">PASO</a>
            <div class="ms-auto">
                {% if user.is_authenticated %}
                    {% if is_owner %}
                        <a href="{% url 'owner_dashboard' %}" class="btn btn-outline-primary btn-sm me-2">Mi Negocio</a>
                    {% else %}
                        <a href="{% url 'client_dashboard' %}" class="btn btn-outline-primary btn-sm me-2">Mis Citas</a>
                    {% endif %}
                    <a href="{% url 'saas_logout' %}" class="btn btn-light btn-sm">Salir</a>
                {% else %}
                    <a href="{% url 'saas_login' %}" class="btn btn-light btn-sm me-2">Entrar</a>
                    <a href="{% url 'register_owner' %}" class="btn btn-dark btn-sm">Soy Negocio</a>
                {% endif %}
            </div>
        </div>
    </nav>
    {% block content %}{% endblock %}
</body>
</html>
""")

create_file('templates/home.html', """
{% extends 'base.html' %}
{% block content %}
<div class="container text-center py-5">
    <h1 class="display-4 fw-bold mb-3">Reserva tu belleza en segundos</h1>
    <p class="lead text-muted mb-4">Encuentra los mejores salones y barberías de tu ciudad.</p>
    <a href="{% url 'marketplace' %}" class="btn btn-gradient btn-lg px-5 py-3 rounded-pill shadow">Explorar Servicios ✂️</a>
</div>
{% endblock %}
""")

create_file('templates/marketplace.html', """
{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <h2 class="fw-bold mb-4">Salones Destacados</h2>
    <div class="row g-4">
        {% for salon in salons %}
        <div class="col-md-4">
            <div class="card border-0 shadow-sm h-100">
                <div class="card-body">
                    <h5 class="fw-bold">{{ salon.name }}</h5>
                    <p class="text-muted small"><i class="fas fa-map-marker-alt"></i> {{ salon.city }}</p>
                    <a href="{% url 'salon_detail' salon.slug %}" class="btn btn-outline-dark w-100">Ver Servicios</a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
""")

create_file('templates/salon_detail.html', """
{% extends 'base.html' %}
{% load humanize %}
{% block content %}
<div class="container py-5">
    <div class="row">
        <div class="col-md-4 mb-4">
            <div class="card border-0 shadow-sm p-4 text-center">
                <h2 class="fw-bold">{{ salon.name }}</h2>
                <p class="text-muted">{{ salon.address }}</p>
                {% if salon.instagram_link %}
                <a href="{{ salon.instagram_link }}" target="_blank" class="btn btn-sm btn-outline-danger"><i class="fab fa-instagram"></i> Instagram</a>
                {% endif %}
            </div>
        </div>
        <div class="col-md-8">
            <h3 class="fw-bold mb-3">Servicios</h3>
            <form action="{% url 'booking_wizard_start' %}" method="POST">
                {% csrf_token %}
                <input type="hidden" name="salon_slug" value="{{ salon.slug }}">
                <div class="list-group mb-4">
                    {% for service in services %}
                    <label class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            <input class="form-check-input me-2" type="checkbox" name="service_ids" value="{{ service.id }}">
                            <span class="fw-bold">{{ service.name }}</span>
                            <small class="d-block text-muted">{{ service.duration_minutes }} min</small>
                        </div>
                        <span class="fw-bold text-success">${{ service.price|intcomma }}</span>
                    </label>
                    {% endfor %}
                </div>
                <button type="submit" class="btn btn-dark w-100 py-3 rounded-pill fw-bold">Reservar Ahora</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
""")

create_file('templates/booking_wizard_datetime.html', """
{% extends 'base.html' %}
{% block content %}
<div class="container py-5 text-center">
    <h3>Elige Fecha y Hora</h3>
    <form action="{% url 'booking_step_contact' %}" method="POST" class="mt-4">
        {% csrf_token %}
        <input type="date" name="date" class="form-control mb-3 w-50 mx-auto" required>
        <select name="time" class="form-select w-50 mx-auto mb-4" required>
            {% for slot in slots %}
            <option value="{{ slot }}">{{ slot }}</option>
            {% endfor %}
        </select>
        <button type="submit" class="btn btn-dark px-5">Siguiente</button>
    </form>
</div>
{% endblock %}
""")

create_file('templates/booking_contact.html', """
{% extends 'base.html' %}
{% load humanize %}
{% block content %}
<div class="container py-5">
    <div class="card shadow border-0 mx-auto" style="max-width: 500px;">
        <div class="card-body p-5">
            <h3 class="fw-bold text-center mb-4">Finalizar Reserva</h3>
            <div class="alert alert-light border">
                <div class="d-flex justify-content-between">
                    <span>Total:</span>
                    <strong>${{ total|intcomma }}</strong>
                </div>
                <div class="d-flex justify-content-between text-success">
                    <span>Abono ({{ porcentaje }}%):</span>
                    <strong>${{ abono|intcomma }}</strong>
                </div>
            </div>
            <form action="{% url 'booking_create' %}" method="POST">
                {% csrf_token %}
                <div class="mb-3">
                    <label>Nombre</label>
                    <input type="text" name="customer_name" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label>Email</label>
                    <input type="email" name="customer_email" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label>WhatsApp</label>
                    <input type="tel" name="customer_phone" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-success w-100 py-3 rounded-pill fw-bold">Confirmar y Pagar Abono</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
""")

create_file('templates/client_dashboard.html', """
{% extends 'base.html' %}
{% load humanize %}
{% block content %}
<div class="container py-5">
    <h2 class="mb-4">Mis Citas</h2>
    <div class="row g-4">
        {% for item in citas %}
        <div class="col-md-6">
            <div class="card border-0 shadow-sm">
                <div class="card-body">
                    <h5 class="fw-bold">{{ item.obj.service.name }}</h5>
                    <p class="text-muted mb-2">{{ item.obj.salon.name }} - {{ item.obj.date }} {{ item.obj.time }}</p>
                    {% if item.obj.status == 'pending_payment' %}
                        <div class="alert alert-warning py-2 small">Pendiente Abono: ${{ item.abono|intcomma }}</div>
                        <a href="{{ item.wa_link }}" target="_blank" class="btn btn-success w-100"><i class="fab fa-whatsapp"></i> Pagar Abono</a>
                    {% else %}
                        <span class="badge bg-success">Confirmada</span>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
""")

create_file('templates/dashboard/owner_dashboard.html', """
{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <h2>Panel de Control - {{ salon.name }}</h2>
    <p>Gestiona tus citas aquí.</p>
</div>
{% endblock %}
""")

create_file('templates/registration/login.html', """
{% extends 'base.html' %}
{% block content %}
<div class="container py-5 text-center">
    <div class="card shadow mx-auto p-4" style="max-width: 400px;">
        <h3 class="mb-3">Iniciar Sesión</h3>
        <form method="POST">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit" class="btn btn-dark w-100">Entrar</button>
        </form>
    </div>
</div>
{% endblock %}
""")

create_file('templates/registration/register_owner.html', """
{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="card shadow mx-auto p-4" style="max-width: 500px;">
        <h3 class="mb-3 text-center">Registra tu Negocio</h3>
        <form method="POST">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit" class="btn btn-dark w-100">Registrar</button>
        </form>
    </div>
</div>
{% endblock %}
""")

# Crear carpetas estáticas vacías
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/images', exist_ok=True)
create_file('static/css/main.css', "/* Estilos vacíos para evitar errores */")

print("✨ GÉNESIS COMPLETADO. El sistema ha renacido limpio y fuerte.")