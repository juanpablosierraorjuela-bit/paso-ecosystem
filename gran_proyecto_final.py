import os
import sys
import textwrap
import subprocess

# ==============================================================================
# CONFIGURACIÓN VISUAL Y UTILIDADES
# ==============================================================================
class Colors:
    OKGREEN = '\033[92m'
    HEADER = '\033[95m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def print_info(msg): print(f"{Colors.HEADER}ℹ️ {msg}{Colors.ENDC}")
def print_success(msg): print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory: os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(textwrap.dedent(content).strip())
    print(f"🔨 Construido: {path}")

print_info("🏗️ INICIANDO CONSTRUCCIÓN DEL ECOSISTEMA FINAL (MODO PRODUCCIÓN)...")

# ==============================================================================
# 1. MODELOS DE DATOS (LA LÓGICA DE NEGOCIO BLINDADA)
# ==============================================================================
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
    
    # Horarios Generales
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
    
    # Horario Almuerzo (Simple)
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
"""
create_file('apps/businesses/models.py', models_content)

# ==============================================================================
# 2. VISTAS INTELIGENTES (EL CEREBRO DEL MARKETPLACE)
# ==============================================================================
views_content = """
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
from .models import Salon, Service, Booking, Employee

User = get_user_model()

# --- UTILIDADES ---
def get_salon(user): return Salon.objects.filter(owner=user).first()

def check_expired_bookings():
    # Auto-cancela citas de más de 60 min sin pago
    try:
        limit = timezone.now() - timedelta(minutes=60)
        Booking.objects.filter(status='pending_payment', created_at__lt=limit).update(status='expired')
    except: pass

def get_available_slots(employee, check_date, duration=60):
    check_expired_bookings()
    salon = employee.salon
    
    # Horario Base
    start_time = salon.open_time
    end_time = salon.close_time
    
    slots = []
    current = datetime.combine(check_date, start_time)
    limit = datetime.combine(check_date, end_time)

    # Filtro: No mostrar pasado si es hoy
    if check_date == date.today():
        now_buffer = datetime.now() + timedelta(minutes=30)
        if current < now_buffer:
            minute = now_buffer.minute
            new_start = now_buffer.replace(minute=30 if minute < 30 else 0, second=0, microsecond=0)
            if minute >= 30: new_start += timedelta(hours=1)
            current = new_start

    # Citas existentes del empleado
    bookings = Booking.objects.filter(
        employee=employee, 
        date=check_date
    ).exclude(status__in=['cancelled', 'expired'])
    
    busy_times = []
    for b in bookings:
        start = datetime.combine(check_date, b.time)
        end = start + timedelta(minutes=b.service.duration_minutes)
        busy_times.append((start, end))

    # Almuerzo del empleado
    if employee.lunch_start and employee.lunch_end:
        l_start = datetime.combine(check_date, employee.lunch_start)
        l_end = datetime.combine(check_date, employee.lunch_end)
        busy_times.append((l_start, l_end))

    # Generación de Slots
    while current + timedelta(minutes=duration) <= limit:
        service_end = current + timedelta(minutes=duration)
        is_free = True
        
        for busy_start, busy_end in busy_times:
            # Si el slot se solapa con algo ocupado
            if (current < busy_end) and (service_end > busy_start):
                is_free = False
                break
        
        if is_free:
            slots.append(current.strftime('%H:%M'))
        
        current += timedelta(minutes=30) # Intervalos de 30 min
    
    return slots

# --- MARKETPLACE & LANDING ---
def home(request):
    return render(request, 'home.html')

def marketplace(request):
    city = request.GET.get('city')
    salons = Salon.objects.all()
    if city:
        salons = salons.filter(city__iexact=city)
    
    cities = Salon.objects.values_list('city', flat=True).distinct().order_by('city')
    return render(request, 'marketplace.html', {
        'salons': salons, 
        'cities': cities, 
        'current_city': city
    })

def salon_detail(request, slug):
    s = get_object_or_404(Salon, slug=slug)
    return render(request, 'salon_detail.html', {
        'salon': s, 
        'services': s.services.all()
    })

# --- FLUJO DE RESERVA (WIZARD) ---
def booking_wizard_start(request): 
    sid = request.POST.getlist('service_ids')
    if not sid:
        messages.error(request, "⚠️ Selecciona al menos un servicio.")
        return redirect('salon_detail', slug=request.POST.get('salon_slug'))
    
    request.session['booking'] = {
        'salon_slug': request.POST.get('salon_slug'),
        'service_ids': sid
    }
    return redirect('booking_step_employee')

def booking_step_employee(request):
    d = request.session.get('booking')
    s = get_object_or_404(Salon, slug=d['salon_slug'])
    
    if request.method == 'POST':
        request.session['booking']['emp_id'] = request.POST.get('employee_id')
        request.session.modified = True
        return redirect('booking_step_datetime')
        
    return render(request, 'booking_wizard_employee.html', {
        'salon': s, 
        'employees': s.employees.filter(is_active=True)
    })

def booking_step_datetime(request):
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    
    date_str = request.GET.get('date', date.today().isoformat())
    check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Calcular duración total
    services = Service.objects.filter(id__in=d['service_ids'])
    total_duration = sum(srv.duration_minutes for srv in services)
    
    emp_id = d.get('emp_id')
    slots = []
    
    # Si eligió empleado específico
    if emp_id and emp_id != 'any':
        emp = Employee.objects.get(id=emp_id)
        slots = get_available_slots(emp, check_date, total_duration)
    else:
        # Si es cualquiera, unimos todos los slots
        all_slots = set()
        for emp in s.employees.filter(is_active=True):
            emp_slots = get_available_slots(emp, check_date, total_duration)
            all_slots.update(emp_slots)
        slots = sorted(list(all_slots))
        
    return render(request, 'booking_wizard_datetime.html', {
        'salon': s,
        'slots': slots,
        'selected_date': date_str,
        'duration': total_duration
    })

def booking_step_contact(request):
    if request.method == 'POST':
        request.session['booking'].update({
            'date': request.POST.get('date'), 
            'time': request.POST.get('time')
        })
        request.session.modified = True
    
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    services = Service.objects.filter(id__in=d['service_ids'])
    
    total = sum(srv.price for srv in services)
    porcentaje = Decimal(s.deposit_percentage) / Decimal(100)
    abono = total * porcentaje
    
    return render(request, 'booking_contact.html', {
        'salon': s,
        'services': services,
        'total': total,
        'abono': abono,
        'porcentaje': s.deposit_percentage
    })

def booking_create(request):
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    email = request.POST['customer_email']
    
    # 1. Registro o Login Automático (Lazy)
    u, created = User.objects.get_or_create(email=email, defaults={'username': email})
    if created: 
        u.set_password('123456')
        u.save()
    login(request, u, backend='django.contrib.auth.backends.ModelBackend')
    
    # 2. Asignar Empleado
    emp_id = d.get('emp_id')
    if emp_id and emp_id != 'any':
        emp = Employee.objects.get(id=emp_id)
    else:
        # Asignar aleatorio o el primero disponible (lógica simple)
        emp = s.employees.filter(is_active=True).first()
        
    # 3. Crear Citas
    first_b = None
    for sid in d['service_ids']:
        b = Booking.objects.create(
            salon=s,
            service_id=sid,
            employee=emp,
            customer_name=request.POST['customer_name'],
            customer_email=email,
            customer_phone=request.POST['customer_phone'],
            date=d['date'],
            time=d['time'],
            status='pending_payment'
        )
        if not first_b: first_b = b
        
    del request.session['booking']
    
    messages.success(request, "¡Reserva Creada! Gestiona tu pago ahora.")
    return redirect('client_dashboard')

# --- PANELES ---
@login_required
def client_dashboard(request):
    check_expired_bookings()
    bookings = Booking.objects.filter(customer_email=request.user.email).order_by('-date', '-time')
    
    citas_data = []
    for b in bookings:
        precio = b.service.price
        porcentaje = Decimal(b.salon.deposit_percentage) / Decimal(100)
        abono = precio * porcentaje
        pendiente = precio - abono
        
        # Generador de Mensaje WhatsApp
        msg = (
            f"👋 Hola {b.salon.name}, soy {b.customer_name}.\\n"
            f"📅 Cita #{b.id} el {b.date} a las {b.time}.\\n"
            f"💅 Servicio: {b.service.name}\\n"
            f"💰 Total: ${precio:,.0f}\\n"
            f"✅ Abono a pagar: ${abono:,.0f}\\n"
            f"¿A qué cuenta transfiero?"
        )
        wa_link = f"https://wa.me/{b.salon.phone}?text={urllib.parse.quote(msg)}"
        
        citas_data.append({
            'obj': b,
            'abono': abono,
            'pendiente': pendiente,
            'wa_link': wa_link
        })
        
    return render(request, 'client_dashboard.html', {'citas': citas_data})

@login_required
def owner_dashboard(request):
    s = get_salon(request.user)
    if not s: return redirect('home') # O redirigir a crear negocio
    
    check_expired_bookings()
    bookings = Booking.objects.filter(salon=s).order_by('-created_at')
    
    return render(request, 'dashboard/owner_dashboard.html', {
        'salon': s, 
        'bookings': bookings
    })

@login_required
def booking_confirm_payment(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id)
    # Seguridad: Solo el dueño del salón puede confirmar
    if b.salon.owner == request.user:
        b.status = 'confirmed'
        b.save()
        messages.success(request, f"Pago confirmado para cita #{b.id}")
    return redirect('owner_dashboard')

# --- AUTH & REGISTRO ---
def saas_login(request):
    if request.user.is_authenticated:
        if Salon.objects.filter(owner=request.user).exists():
            return redirect('owner_dashboard')
        return redirect('client_dashboard')
        
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if Salon.objects.filter(owner=request.user).exists():
                return redirect('owner_dashboard')
            return redirect('client_dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'registration/login.html', {'form': form})

def register_owner(request):
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                u = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name']
                )
                u.role = 'ADMIN'
                u.save()
                
                s = Salon.objects.create(
                    owner=u,
                    name=form.cleaned_data['nombre_negocio'],
                    city=form.cleaned_data['ciudad'],
                    phone=form.cleaned_data['whatsapp'],
                    # Se crean horarios por defecto automáticamente o aquí
                )
                login(request, u, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('owner_dashboard')
    else:
        form = OwnerRegistrationForm()
    return render(request, 'registration/register_owner.html', {'form': form})

def saas_logout(request):
    logout(request)
    return redirect('home')
"""
create_file('apps/businesses/views.py', views_content)

# ==============================================================================
# 3. TEMPLATES MODERNOS (DISEÑO ELEGANTE Y RESPONSIVO)
# ==============================================================================

# BASE HTML (Con Bootstrap y FontAwesome)
create_file('templates/base.html', """
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paso Marketplace | Tu Belleza, Tu Tiempo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f8f9fa; color: #333; }
        .navbar { background: white; padding: 1rem 0; }
        .navbar-brand { font-weight: 800; font-size: 1.5rem; color: #111 !important; letter-spacing: -1px; }
        .btn-primary { background-color: #111; border-color: #111; padding: 0.6rem 1.2rem; font-weight: 600; border-radius: 8px; }
        .btn-primary:hover { background-color: #333; border-color: #333; }
        .btn-success { background-color: #25D366; border: none; font-weight: 600; } /* WhatsApp Green */
        .btn-success:hover { background-color: #1ebc57; }
        .card { border: none; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: transform 0.2s; }
        .card:hover { transform: translateY(-3px); }
        .badge-status { padding: 0.5em 0.8em; border-radius: 6px; font-weight: 600; font-size: 0.75rem; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light border-bottom">
        <div class="container">
            <a class="navbar-brand" href="{% url 'home' %}">PASO.</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-center">
                    {% if user.is_authenticated %}
                        {% if is_owner %}
                            <li class="nav-item"><a href="{% url 'owner_dashboard' %}" class="nav-link fw-bold text-dark">Mi Negocio</a></li>
                        {% else %}
                            <li class="nav-item"><a href="{% url 'client_dashboard' %}" class="nav-link fw-bold text-dark">Mis Citas</a></li>
                        {% endif %}
                        <li class="nav-item ms-3"><a href="{% url 'saas_logout' %}" class="btn btn-outline-danger btn-sm">Salir</a></li>
                    {% else %}
                        <li class="nav-item"><a href="{% url 'saas_login' %}" class="nav-link">Iniciar Sesión</a></li>
                        <li class="nav-item ms-3"><a href="{% url 'register_owner' %}" class="btn btn-primary btn-sm">Soy Dueño</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    {% if messages %}
        <div class="container mt-3">
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        </div>
    {% endif %}

    <div class="min-vh-100">
        {% block content %}{% endblock %}
    </div>

    <footer class="bg-white py-4 mt-5 border-top">
        <div class="container text-center text-muted small">
            &copy; 2026 Paso Ecosystem. Hecho con ❤️ para emprendedores.
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")

# HOME
create_file('templates/home.html', """
{% extends 'base.html' %}
{% block content %}
<div class="container text-center d-flex flex-column align-items-center justify-content-center" style="height: 70vh;">
    <h1 class="display-3 fw-bold mb-3" style="letter-spacing: -2px;">Belleza a un clic.</h1>
    <p class="lead text-muted mb-5" style="max-width: 600px;">
        Reserva en los mejores salones, barberías y spas de tu ciudad sin llamadas ni esperas.
    </p>
    
    <div class="d-flex gap-3">
        <a href="{% url 'marketplace' %}" class="btn btn-primary btn-lg px-5 py-3 shadow-lg">
            <i class="fas fa-search me-2"></i> Buscar Servicios
        </a>
        <a href="{% url 'register_owner' %}" class="btn btn-outline-dark btn-lg px-5 py-3">
            Registrar mi Negocio
        </a>
    </div>
    
    <div class="mt-5 pt-5 text-muted small">
        <i class="fas fa-check-circle text-success me-1"></i> Reserva 24/7 &nbsp;&nbsp;
        <i class="fas fa-check-circle text-success me-1"></i> Pagos Seguros &nbsp;&nbsp;
        <i class="fas fa-check-circle text-success me-1"></i> Confirmación Inmediata
    </div>
</div>
{% endblock %}
""")

# MARKETPLACE (Con filtro ciudad)
create_file('templates/marketplace.html', """
{% extends 'base.html' %}
{% block content %}
<div class="bg-light py-5">
    <div class="container">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="fw-bold m-0">Explorar Negocios 💈</h2>
            
            <form class="d-flex" method="GET">
                <select name="city" class="form-select me-2" onchange="this.form.submit()">
                    <option value="">Todas las ciudades</option>
                    {% for city in cities %}
                    <option value="{{ city }}" {% if current_city == city %}selected{% endif %}>{{ city }}</option>
                    {% endfor %}
                </select>
            </form>
        </div>

        <div class="row g-4">
            {% for salon in salons %}
            <div class="col-md-6 col-lg-4">
                <div class="card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h4 class="card-title fw-bold mb-0">{{ salon.name }}</h4>
                            {% if salon.instagram_link %}
                            <a href="{{ salon.instagram_link }}" target="_blank" class="text-danger fs-4"><i class="fab fa-instagram"></i></a>
                            {% endif %}
                        </div>
                        <p class="text-muted small mb-2"><i class="fas fa-map-marker-alt me-1"></i> {{ salon.city }}</p>
                        <p class="text-muted small"><i class="fas fa-clock me-1"></i> {{ salon.open_time }} - {{ salon.close_time }}</p>
                        
                        <hr>
                        <a href="{% url 'salon_detail' salon.slug %}" class="btn btn-dark w-100 fw-bold">Ver Servicios y Reservar</a>
                    </div>
                </div>
            </div>
            {% empty %}
            <div class="col-12 text-center py-5">
                <h3 class="text-muted">No encontramos negocios aquí aún. 😢</h3>
                <p>¡Sé el primero en registrar el tuyo!</p>
                <a href="{% url 'register_owner' %}" class="btn btn-primary mt-3">Registrar Negocio</a>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
<script>
    // Geolocalización Simulada (Mejora futura)
    document.addEventListener("DOMContentLoaded", function() {
        if (!"{{ current_city }}") {
            // Aquí podríamos preguntar al usuario su ubicación
        }
    });
</script>
{% endblock %}
""")

# CLIENT DASHBOARD (Con botones de pago inteligentes)
create_file('templates/client_dashboard.html', """
{% extends 'base.html' %}
{% load humanize %}
{% block content %}
<div class="container py-5">
    <h2 class="fw-bold mb-4">Mis Citas 📅</h2>
    
    <div class="row g-4">
        {% for item in citas %}
        <div class="col-md-6 col-lg-4">
            <div class="card h-100 border-0 shadow-sm">
                <div class="card-header bg-white border-bottom-0 pt-4 pb-0 d-flex justify-content-between">
                    <small class="text-muted">#{{ item.obj.id }}</small>
                    {% if item.obj.status == 'pending_payment' %}
                        <span class="badge bg-warning text-dark">🟡 Pendiente Abono</span>
                    {% elif item.obj.status == 'confirmed' %}
                        <span class="badge bg-success">🟢 Confirmada</span>
                    {% elif item.obj.status == 'expired' %}
                        <span class="badge bg-secondary">⚫ Expirada</span>
                    {% else %}
                        <span class="badge bg-danger">Cancelada</span>
                    {% endif %}
                </div>
                
                <div class="card-body">
                    <h5 class="fw-bold mt-2">{{ item.obj.service.name }}</h5>
                    <p class="text-muted mb-1"><i class="fas fa-store me-1"></i> {{ item.obj.salon.name }}</p>
                    <p class="text-muted mb-3"><i class="fas fa-clock me-1"></i> {{ item.obj.date }} a las {{ item.obj.time }}</p>
                    
                    <div class="bg-light p-3 rounded-3 mb-3">
                        <div class="d-flex justify-content-between mb-1">
                            <span>Total:</span>
                            <strong>${{ item.obj.service.price|intcomma }}</strong>
                        </div>
                        <div class="d-flex justify-content-between text-success">
                            <span>Abono ({{ item.obj.salon.deposit_percentage }}%):</span>
                            <strong>${{ item.abono|intcomma }}</strong>
                        </div>
                    </div>

                    {% if item.obj.status == 'pending_payment' %}
                        <a href="{{ item.wa_link }}" target="_blank" class="btn btn-success w-100 fw-bold mb-2">
                            <i class="fab fa-whatsapp me-2"></i> Pagar Abono
                        </a>
                        <small class="text-muted d-block text-center" style="font-size: 0.8rem;">
                            Se abrirá WhatsApp con los datos para transferir.
                        </small>
                    {% elif item.obj.status == 'confirmed' %}
                        <button class="btn btn-outline-success w-100" disabled>
                            <i class="fas fa-check-circle me-2"></i> Todo Listo
                        </button>
                        <p class="text-center mt-2 small text-muted">
                            Pendiente en local: <strong>${{ item.pendiente|intcomma }}</strong>
                        </p>
                    {% endif %}
                </div>
            </div>
        </div>
        {% empty %}
        <div class="col-12 text-center py-5">
            <h4 class="text-muted">Aún no tienes citas.</h4>
            <a href="{% url 'marketplace' %}" class="btn btn-primary mt-3">Ir a Reservar</a>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
""")

# OWNER DASHBOARD (Gestión)
create_file('templates/dashboard/owner_dashboard.html', """
{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h2 class="fw-bold">{{ salon.name }}</h2>
            <p class="text-muted m-0">Panel de Control</p>
        </div>
        <div>
            <button class="btn btn-outline-dark me-2"><i class="fas fa-cog"></i> Configuración</button>
            <button class="btn btn-primary"><i class="fas fa-plus"></i> Nuevo Servicio</button>
        </div>
    </div>

    <div class="card shadow-sm mb-4">
        <div class="card-header bg-white py-3">
            <h5 class="m-0 fw-bold">Próximas Citas</h5>
        </div>
        <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
                <thead class="bg-light">
                    <tr>
                        <th>#</th>
                        <th>Cliente</th>
                        <th>Servicio</th>
                        <th>Fecha/Hora</th>
                        <th>Empleado</th>
                        <th>Estado</th>
                        <th>Acción</th>
                    </tr>
                </thead>
                <tbody>
                    {% for b in bookings %}
                    <tr>
                        <td>{{ b.id }}</td>
                        <td>
                            <div class="fw-bold">{{ b.customer_name }}</div>
                            <small class="text-muted">{{ b.customer_phone }}</small>
                        </td>
                        <td>{{ b.service.name }}</td>
                        <td>{{ b.date }} <span class="badge bg-light text-dark border">{{ b.time }}</span></td>
                        <td>{{ b.employee.name }}</td>
                        <td>
                            {% if b.status == 'pending_payment' %}
                                <span class="badge bg-warning text-dark">Pendiente Pago</span>
                            {% elif b.status == 'confirmed' %}
                                <span class="badge bg-success">Confirmada</span>
                            {% else %}
                                <span class="badge bg-secondary">{{ b.status }}</span>
                            {% endif %}
                        </td>
                        <td>
                            {% if b.status == 'pending_payment' %}
                            <a href="{% url 'booking_confirm_payment' b.id %}" class="btn btn-sm btn-outline-success" onclick="return confirm('¿Confirmas que recibiste el dinero?')">
                                <i class="fas fa-check"></i> Verificar Pago
                            </a>
                            {% endif %}
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="7" class="text-center py-4 text-muted">No hay citas registradas.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
""")

print_success("¡PLAN MAESTRO EJECUTADO! Archivos generados.")
print_info("Ahora ejecuta los comandos de git para subir esto a Render.")