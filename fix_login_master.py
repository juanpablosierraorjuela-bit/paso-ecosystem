import os
import textwrap
import subprocess

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory: os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(textwrap.dedent(content).strip())
    print(f"✅ Actualizado: {path}")

print("🔐 RECONSTRUYENDO SISTEMA DE ACCESO (LOGIN INTELIGENTE)...")

# ==============================================================================
# 1. VIEWS.PY - LÓGICA DE LOGIN INTELIGENTE
# ==============================================================================
# Aquí está la magia: Detectamos si el usuario tiene un Salón y lo redirigimos.
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
from .models import Salon, Service, Booking, Employee, Schedule, OpeningHours

User = get_user_model()

# --- UTILIDADES ---
def get_salon(user): return Salon.objects.filter(owner=user).first()

def check_expired_bookings():
    try:
        limit = timezone.now() - timedelta(minutes=60)
        Booking.objects.filter(status='pending_payment', created_at__lt=limit).update(status='expired')
    except: pass

def get_available_slots(employee, check_date, duration=60):
    check_expired_bookings()
    salon = employee.salon
    day_idx = check_date.weekday()
    opening = OpeningHours.objects.filter(salon=salon, day_of_week=day_idx, is_closed=False).first()
    if not opening: return []
    
    sched = Schedule.objects.filter(employee=employee, day_of_week=day_idx, is_active=True).first()
    if not sched: return []
    
    start_limit = max(opening.start_time, sched.start_time)
    end_limit = min(opening.end_time, sched.end_time)
    
    slots = []
    current = datetime.combine(check_date, start_limit)
    limit = datetime.combine(check_date, end_limit)

    if check_date == date.today():
        now_buffer = datetime.now() + timedelta(minutes=30)
        if current < now_buffer:
            minute = now_buffer.minute
            new_start = now_buffer.replace(minute=30 if minute < 30 else 0, second=0, microsecond=0)
            if minute >= 30: new_start += timedelta(hours=1)
            current = new_start

    bookings = Booking.objects.filter(employee=employee, date=check_date).exclude(status__in=['cancelled', 'expired'])
    busy_times = []
    for b in bookings:
        start = datetime.combine(check_date, b.time)
        end = start + timedelta(minutes=b.service.duration_minutes)
        busy_times.append((start, end))

    if employee.lunch_start and employee.lunch_end:
        l_start = datetime.combine(check_date, employee.lunch_start)
        l_end = datetime.combine(check_date, employee.lunch_end)
        busy_times.append((l_start, l_end))

    while current + timedelta(minutes=duration) <= limit:
        service_end = current + timedelta(minutes=duration)
        is_free = True
        for busy_start, busy_end in busy_times:
            if (current < busy_end) and (service_end > busy_start):
                is_free = False
                break
        if is_free: slots.append(current.strftime('%H:%M'))
        current += timedelta(minutes=30)
    return slots

# --- LOGIN INTELIGENTE ---
def saas_login(request):
    # Si ya está logueado, redirigir según rol
    if request.user.is_authenticated:
        if Salon.objects.filter(owner=request.user).exists():
            return redirect('owner_dashboard')
        return redirect('client_dashboard')

    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # LÓGICA DE REDIRECCIÓN
            if Salon.objects.filter(owner=user).exists():
                return redirect('owner_dashboard')
            else:
                return redirect('client_dashboard')
    else:
        form = UserLoginForm()
    
    return render(request, 'registration/login.html', {'form': form})

def saas_logout(request):
    logout(request)
    return redirect('home')

# --- REGISTRO ---
def register_owner(request):
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                u = User.objects.create_user(
                    username=form.cleaned_data['email'], email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'], first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name']
                )
                u.role = 'ADMIN'; u.save()
                
                ig_user = form.cleaned_data['instagram']
                ig_link = f"https://instagram.com/{ig_user}" if ig_user else ""
                
                Salon.objects.create(
                    owner=u, name=form.cleaned_data['nombre_negocio'],
                    city=form.cleaned_data['ciudad'], address=form.cleaned_data['direccion'],
                    phone=form.cleaned_data['whatsapp'], instagram_link=ig_link
                )
                login(request, u, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('owner_dashboard')
    else:
        form = OwnerRegistrationForm()
    return render(request, 'registration/register_owner.html', {'form': form})

# --- PANELES ---
@login_required
def owner_dashboard(request):
    s = get_salon(request.user)
    if not s: return redirect('client_dashboard') # Si no es dueño, va a cliente
    
    check_expired_bookings()
    bookings = Booking.objects.filter(salon=s).order_by('-created_at')
    
    today_bookings = bookings.filter(date=date.today(), status='confirmed').count()
    pending_bookings = bookings.filter(status='pending_payment').count()
    
    return render(request, 'dashboard/owner_dashboard.html', {
        'salon': s, 'bookings': bookings, 
        'today_count': today_bookings, 'pending_count': pending_bookings
    })

@login_required
def client_dashboard(request):
    check_expired_bookings()
    bookings = Booking.objects.filter(customer_email=request.user.email).order_by('-date', '-time')
    citas_data = []
    for b in bookings:
        precio = b.service.price
        porcentaje = Decimal(b.salon.deposit_percentage) / Decimal(100)
        abono = precio * porcentaje
        msg = f"👋 Hola {b.salon.name}, soy {b.customer_name}.\\n📅 Cita #{b.id} el {b.date} a las {b.time}.\\n💰 Total: ${precio:,.0f}\\n✅ Abono a pagar: ${abono:,.0f}"
        wa_link = f"https://wa.me/{b.salon.phone}?text={urllib.parse.quote(msg)}"
        citas_data.append({'obj': b, 'abono': abono, 'pendiente': precio - abono, 'wa_link': wa_link})
    return render(request, 'client_dashboard.html', {'citas': citas_data})

@login_required
def booking_confirm_payment(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id)
    if b.salon.owner == request.user:
        b.status = 'confirmed'; b.save()
        messages.success(request, "Pago verificado exitosamente.")
    return redirect('owner_dashboard')

# --- GESTIÓN ADICIONAL ---
@login_required
def owner_services(request):
    s = get_salon(request.user)
    if not s: return redirect('home')
    
    if request.method == 'POST':
        if 'delete_id' in request.POST:
            Service.objects.filter(id=request.POST['delete_id'], salon=s).delete()
            messages.success(request, "Servicio eliminado.")
        else:
            form = ServiceForm(request.POST)
            if form.is_valid():
                srv = form.save(commit=False)
                srv.salon = s; srv.save()
                messages.success(request, "Servicio agregado.")
        return redirect('owner_services')
    
    return render(request, 'dashboard/owner_services.html', {'salon': s, 'services': s.services.all(), 'form': ServiceForm()})

@login_required
def owner_employees(request):
    s = get_salon(request.user)
    if not s: return redirect('home')
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['email'], email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'], first_name=form.cleaned_data['name']
                )
                user.role = 'EMPLOYEE'; user.save()
                
                emp = Employee.objects.create(user=user, salon=s, name=form.cleaned_data['name'])
                for day in range(0, 6):
                    Schedule.objects.create(employee=emp, day_of_week=day, start_time=form.cleaned_data['start_time'], end_time=form.cleaned_data['end_time'])
                messages.success(request, "Empleado registrado.")
        return redirect('owner_employees')
    
    return render(request, 'dashboard/owner_employees.html', {'salon': s, 'employees': s.employees.all(), 'form': EmployeeCreationForm()})

@login_required
def owner_settings(request):
    s = get_salon(request.user)
    if not s: return redirect('home')
    
    if request.method == 'POST':
        if 'update_salon' in request.POST:
            form = SalonConfigForm(request.POST, instance=s)
            if form.is_valid(): form.save(); messages.success(request, "Datos actualizados.")
        elif 'update_hours' in request.POST:
            for day in range(7):
                is_closed = request.POST.get(f'day_{day}_open') is None
                start = request.POST.get(f'day_{day}_start', '08:00')
                end = request.POST.get(f'day_{day}_end', '20:00')
                OpeningHours.objects.update_or_create(salon=s, day_of_week=day, defaults={'start_time': start, 'end_time': end, 'is_closed': is_closed})
            messages.success(request, "Horarios actualizados.")
        return redirect('owner_settings')
    
    hours = []
    days_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    for i, name in enumerate(days_names):
        h = OpeningHours.objects.filter(salon=s, day_of_week=i).first()
        hours.append({'id': i, 'name': name, 'start': h.start_time if h else s.open_time, 'end': h.end_time if h else s.close_time, 'is_closed': h.is_closed if h else False})
        
    return render(request, 'dashboard/owner_settings.html', {'salon': s, 'form': SalonConfigForm(instance=s), 'hours': hours})

# --- VISTAS PÚBLICAS ---
def home(request): return render(request, 'home.html')
def marketplace(request):
    city = request.GET.get('city'); salons = Salon.objects.all()
    if city: salons = salons.filter(city__iexact=city)
    return render(request, 'marketplace.html', {'salons': salons, 'cities': Salon.objects.values_list('city', flat=True).distinct()})
def salon_detail(request, slug):
    s = get_object_or_404(Salon, slug=slug)
    return render(request, 'salon_detail.html', {'salon': s, 'services': s.services.all()})

# --- WIZARD ---
def booking_wizard_start(request): 
    sid = request.POST.getlist('service_ids')
    request.session['booking']={'salon_slug':request.POST.get('salon_slug'), 'service_ids':sid}
    return redirect('booking_step_employee')
def booking_step_employee(request):
    d=request.session.get('booking'); s=Salon.objects.get(slug=d['salon_slug'])
    if request.method=='POST': request.session['booking']['emp_id']=request.POST.get('employee_id'); request.session.modified=True; return redirect('booking_step_datetime')
    return render(request,'booking_wizard_employee.html',{'salon':s,'employees':s.employees.filter(is_active=True)})
def booking_step_datetime(request):
    d=request.session.get('booking'); s=Salon.objects.get(slug=d['salon_slug']); emp_id=d.get('emp_id')
    check_date=datetime.strptime(request.GET.get('date',date.today().isoformat()),'%Y-%m-%d').date()
    srvs=Service.objects.filter(id__in=d['service_ids']); total=sum(sv.duration_minutes for sv in srvs)
    if emp_id and emp_id!='any': slots=get_available_slots(Employee.objects.get(id=emp_id),check_date,total)
    else: slots=[]; [slots.extend(get_available_slots(e,check_date,total)) for e in s.employees.filter(is_active=True)]; slots=sorted(list(set(slots)))
    return render(request,'booking_wizard_datetime.html',{'salon':s,'slots':slots,'selected_date':check_date,'duration':total})
def booking_step_contact(request):
    if request.method=='POST': request.session['booking'].update({'date':request.POST.get('date'),'time':request.POST.get('time')}); request.session.modified=True
    d=request.session.get('booking'); s=Salon.objects.get(slug=d['salon_slug']); srvs=Service.objects.filter(id__in=d['service_ids'])
    total=sum(sv.price for sv in srvs); porc=Decimal(s.deposit_percentage)/100; return render(request,'booking_contact.html',{'salon':s,'total':total,'abono':total*porc,'porcentaje':s.deposit_percentage})
def booking_create(request):
    d=request.session.get('booking'); s=Salon.objects.get(slug=d['salon_slug']); email=request.POST['customer_email']
    u,c=User.objects.get_or_create(email=email,defaults={'username':email}); 
    if c: u.set_password('123456'); u.save()
    login(request,u,backend='django.contrib.auth.backends.ModelBackend')
    emp_id=d.get('emp_id'); emp=Employee.objects.get(id=emp_id) if emp_id and emp_id!='any' else s.employees.first()
    for sid in d['service_ids']: Booking.objects.create(salon=s,service_id=sid,employee=emp,customer_name=request.POST['customer_name'],customer_email=email,customer_phone=request.POST['customer_phone'],date=d['date'],time=d['time'])
    return redirect('client_dashboard')
"""
create_file('apps/businesses/views.py', views_content)

# ==============================================================================
# 2. TEMPLATE LOGIN DE LUJO (A juego con el registro)
# ==============================================================================
login_template = """
{% extends 'base.html' %}
{% load static %}
{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
            
            <div class="card border-0 shadow-lg rounded-4 overflow-hidden">
                <div class="card-header bg-dark text-white text-center py-5" style="background: linear-gradient(135deg, #000000 0%, #333333 100%);">
                    <img src="{% static 'images/favicon.svg' %}" alt="Logo" width="50" height="50" class="mb-3 opacity-75">
                    <h3 class="fw-bold mb-1">Bienvenido de Nuevo</h3>
                    <p class="text-white-50 small mb-0">Ingresa a tu ecosistema.</p>
                </div>

                <div class="card-body p-5">
                    <form method="POST">
                        {% csrf_token %}
                        
                        <div class="form-floating mb-3">
                            {{ form.username }}
                            <label for="{{ form.username.id_for_label }}">{{ form.username.label }}</label>
                        </div>
                        
                        <div class="form-floating mb-4">
                            {{ form.password }}
                            <label for="{{ form.password.id_for_label }}">{{ form.password.label }}</label>
                        </div>

                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-dark btn-lg py-3 rounded-3 fw-bold shadow-sm">
                                Iniciar Sesión <i class="fas fa-arrow-right ms-2"></i>
                            </button>
                        </div>
                    </form>
                </div>

                <div class="card-footer bg-light text-center py-3">
                    <p class="mb-0 text-muted small">
                        ¿Nuevo aquí? <a href="{% url 'register_owner' %}" class="fw-bold text-dark text-decoration-none">Registra tu Negocio</a>
                    </p>
                </div>
            </div>
            
            <p class="text-center text-muted mt-4 small">
                <i class="fas fa-shield-alt me-1"></i> Acceso Seguro SSL
            </p>
        </div>
    </div>
</div>
{% endblock %}
"""
create_file('templates/registration/login.html', login_template)

# ==============================================================================
# 3. SETTINGS.PY BLINDADO (Aseguramos que no haya bucles de redirección)
# ==============================================================================
# Este bloque es VITAL para que Render no falle con "Too many redirects"
settings_fix = """
from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-genesis-key-2026')

IN_RENDER = 'RENDER' in os.environ
if IN_RENDER:
    DEBUG = False
    ALLOWED_HOSTS = ['*']
else:
    DEBUG = True
    ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'django.contrib.humanize', 'rest_framework', 'corsheaders',
    'apps.core_saas', 'apps.businesses',
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
                'django.template.context_processors.debug', 'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages',
                'apps.businesses.context_processors.owner_check',
            ],
        },
    },
]

WSGI_APPLICATION = 'paso_ecosystem.wsgi.application'

DATABASES = {'default': dj_database_url.config(default='sqlite:///db.sqlite3', conn_max_age=600)}

# --- SEGURIDAD SSL (FIX DEFINITIVO) ---
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
if IN_RENDER:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if RENDER_EXTERNAL_HOSTNAME:
        CSRF_TRUSTED_ORIGINS = ['https://' + RENDER_EXTERNAL_HOSTNAME]

AUTH_PASSWORD_VALIDATORS = [] 
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
LOGIN_REDIRECT_URL = 'owner_dashboard' # Por defecto intentamos dueño, pero views.py lo corrige
LOGOUT_REDIRECT_URL = 'home'
"""
create_file('paso_ecosystem/settings.py', settings_fix)

# ==============================================================================
# SUBIDA
# ==============================================================================
print("🤖 Subiendo Login Maestro a GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Feature: Smart Login redirection (Owner vs Client) and Luxury Login Design"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("🚀 ¡ENVIADO! Espera el deploy y tendrás el mejor login de la historia.")
except Exception as e:
    print(f"⚠️ Error git: {e}")