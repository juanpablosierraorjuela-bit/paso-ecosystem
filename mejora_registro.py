import os
import textwrap
import subprocess
import sys

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory: os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(textwrap.dedent(content).strip())
    print(f"💎 Refinado: {path}")

print("🚀 INICIANDO PROTOCOLO DE LUJO: REGISTRO DE DUEÑOS v2.0...")

# ==============================================================================
# 1. FORMS.PY (CON LISTA DE CIUDADES Y PLACEHOLDERS)
# ==============================================================================
forms_content = """
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))

class OwnerRegistrationForm(forms.Form):
    CIUDADES_COLOMBIA = [
        ('', 'Selecciona tu Ciudad...'),
        ('Bogotá', 'Bogotá'),
        ('Medellín', 'Medellín'),
        ('Cali', 'Cali'),
        ('Barranquilla', 'Barranquilla'),
        ('Cartagena', 'Cartagena'),
        ('Tunja', 'Tunja'),
        ('Bucaramanga', 'Bucaramanga'),
        ('Pereira', 'Pereira'),
        ('Manizales', 'Manizales'),
        ('Cúcuta', 'Cúcuta'),
        ('Ibagué', 'Ibagué'),
        ('Santa Marta', 'Santa Marta'),
        ('Villavicencio', 'Villavicencio'),
        ('Pasto', 'Pasto'),
        ('Montería', 'Montería'),
        ('Neiva', 'Neiva'),
        ('Armenia', 'Armenia'),
        ('Popayán', 'Popayán'),
        ('Valledupar', 'Valledupar'),
        ('Sincelejo', 'Sincelejo'),
        ('Sogamoso', 'Sogamoso'),
        ('Duitama', 'Duitama'),
        ('Otra', 'Otra Ciudad'),
    ]

    # Datos Personales
    first_name = forms.CharField(
        label="Tu Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pablo'})
    )
    last_name = forms.CharField(
        label="Tu Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Sierra'})
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tuemail@ejemplo.com'})
    )
    password = forms.CharField(
        label="Contraseña Segura",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '******'})
    )

    # Datos del Negocio
    nombre_negocio = forms.CharField(
        label="Nombre del Negocio",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Barbería El Imperio'})
    )
    ciudad = forms.ChoiceField(
        label="Ciudad",
        choices=CIUDADES_COLOMBIA,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    direccion = forms.CharField(
        label="Dirección del Local",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cra 10 # 20-30, Centro'})
    )
    whatsapp = forms.CharField(
        label="WhatsApp del Negocio (Sin símbolos)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 573220317702'})
    )
    instagram = forms.CharField(
        label="Usuario de Instagram (Opcional)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: pasotunja'})
    )
"""
create_file('apps/businesses/forms.py', forms_content)

# ==============================================================================
# 2. VIEWS.PY (ACTUALIZADO PARA GUARDAR LA DIRECCIÓN)
# ==============================================================================
# Nota: Reescribimos todo el archivo para asegurar consistencia, manteniendo las otras vistas.
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
    try:
        limit = timezone.now() - timedelta(minutes=60)
        Booking.objects.filter(status='pending_payment', created_at__lt=limit).update(status='expired')
    except: pass

def get_available_slots(employee, check_date, duration=60):
    check_expired_bookings()
    salon = employee.salon
    start_time = salon.open_time
    end_time = salon.close_time
    slots = []
    current = datetime.combine(check_date, start_time)
    limit = datetime.combine(check_date, end_time)

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

# --- MARKETPLACE & LANDING ---
def home(request): return render(request, 'home.html')

def marketplace(request):
    city = request.GET.get('city')
    salons = Salon.objects.all()
    if city: salons = salons.filter(city__iexact=city)
    cities = Salon.objects.values_list('city', flat=True).distinct().order_by('city')
    return render(request, 'marketplace.html', {'salons': salons, 'cities': cities, 'current_city': city})

def salon_detail(request, slug):
    s = get_object_or_404(Salon, slug=slug)
    return render(request, 'salon_detail.html', {'salon': s, 'services': s.services.all()})

# --- FLUJO DE RESERVA ---
def booking_wizard_start(request): 
    sid = request.POST.getlist('service_ids')
    if not sid:
        messages.error(request, "⚠️ Selecciona al menos un servicio.")
        return redirect('salon_detail', slug=request.POST.get('salon_slug'))
    request.session['booking'] = {'salon_slug': request.POST.get('salon_slug'), 'service_ids': sid}
    return redirect('booking_step_employee')

def booking_step_employee(request):
    d = request.session.get('booking')
    s = get_object_or_404(Salon, slug=d['salon_slug'])
    if request.method == 'POST':
        request.session['booking']['emp_id'] = request.POST.get('employee_id')
        request.session.modified = True
        return redirect('booking_step_datetime')
    return render(request, 'booking_wizard_employee.html', {'salon': s, 'employees': s.employees.filter(is_active=True)})

def booking_step_datetime(request):
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    date_str = request.GET.get('date', date.today().isoformat())
    check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    services = Service.objects.filter(id__in=d['service_ids'])
    total_duration = sum(srv.duration_minutes for srv in services)
    
    emp_id = d.get('emp_id')
    slots = []
    if emp_id and emp_id != 'any':
        emp = Employee.objects.get(id=emp_id)
        slots = get_available_slots(emp, check_date, total_duration)
    else:
        all_slots = set()
        for emp in s.employees.filter(is_active=True):
            emp_slots = get_available_slots(emp, check_date, total_duration)
            all_slots.update(emp_slots)
        slots = sorted(list(all_slots))
        
    return render(request, 'booking_wizard_datetime.html', {'salon': s, 'slots': slots, 'selected_date': date_str, 'duration': total_duration})

def booking_step_contact(request):
    if request.method == 'POST':
        request.session['booking'].update({'date': request.POST.get('date'), 'time': request.POST.get('time')})
        request.session.modified = True
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    services = Service.objects.filter(id__in=d['service_ids'])
    total = sum(srv.price for srv in services)
    porcentaje = Decimal(s.deposit_percentage) / Decimal(100)
    abono = total * porcentaje
    return render(request, 'booking_contact.html', {'salon': s, 'services': services, 'total': total, 'abono': abono, 'porcentaje': s.deposit_percentage})

def booking_create(request):
    d = request.session.get('booking')
    s = Salon.objects.get(slug=d['salon_slug'])
    email = request.POST['customer_email']
    u, created = User.objects.get_or_create(email=email, defaults={'username': email})
    if created: u.set_password('123456'); u.save()
    login(request, u, backend='django.contrib.auth.backends.ModelBackend')
    
    emp_id = d.get('emp_id')
    emp = Employee.objects.get(id=emp_id) if (emp_id and emp_id != 'any') else s.employees.filter(is_active=True).first()
    
    for sid in d['service_ids']:
        Booking.objects.create(
            salon=s, service_id=sid, employee=emp, customer_name=request.POST['customer_name'],
            customer_email=email, customer_phone=request.POST['customer_phone'], date=d['date'], time=d['time']
        )
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
        msg = f"👋 Hola {b.salon.name}, soy {b.customer_name}.\\n📅 Cita #{b.id} el {b.date} a las {b.time}.\\n💰 Total: ${precio:,.0f}\\n✅ Abono a pagar: ${abono:,.0f}"
        wa_link = f"https://wa.me/{b.salon.phone}?text={urllib.parse.quote(msg)}"
        citas_data.append({'obj': b, 'abono': abono, 'pendiente': pendiente, 'wa_link': wa_link})
    return render(request, 'client_dashboard.html', {'citas': citas_data})

@login_required
def owner_dashboard(request):
    s = get_salon(request.user)
    if not s: return redirect('home')
    check_expired_bookings()
    bookings = Booking.objects.filter(salon=s).order_by('-created_at')
    return render(request, 'dashboard/owner_dashboard.html', {'salon': s, 'bookings': bookings})

@login_required
def booking_confirm_payment(request, booking_id):
    b = get_object_or_404(Booking, id=booking_id)
    if b.salon.owner == request.user:
        b.status = 'confirmed'; b.save()
        messages.success(request, f"Pago confirmado para cita #{b.id}")
    return redirect('owner_dashboard')

# --- AUTH ACTUALIZADO (Con Address y link de Instagram) ---
def saas_login(request):
    if request.user.is_authenticated:
        if Salon.objects.filter(owner=request.user).exists(): return redirect('owner_dashboard')
        return redirect('client_dashboard')
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if Salon.objects.filter(owner=request.user).exists(): return redirect('owner_dashboard')
            return redirect('client_dashboard')
    else: form = UserLoginForm()
    return render(request, 'registration/login.html', {'form': form})

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
                
                # Crear Link de Instagram
                ig_user = form.cleaned_data['instagram']
                ig_link = f"https://instagram.com/{ig_user}" if ig_user else ""
                
                Salon.objects.create(
                    owner=u,
                    name=form.cleaned_data['nombre_negocio'],
                    city=form.cleaned_data['ciudad'],
                    address=form.cleaned_data['direccion'],
                    phone=form.cleaned_data['whatsapp'],
                    instagram_link=ig_link
                )
                login(request, u, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('owner_dashboard')
    else:
        form = OwnerRegistrationForm()
    return render(request, 'registration/register_owner.html', {'form': form})

def saas_logout(request): logout(request); return redirect('home')
"""
create_file('apps/businesses/views.py', views_content)

# ==============================================================================
# 3. TEMPLATE LUJOSO (MODERNO, LIMPIO Y COMPLETO)
# ==============================================================================
template_content = """
{% extends 'base.html' %}
{% load static %}
{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-lg-8 col-xl-6">
            
            <div class="card border-0 shadow-lg rounded-4 overflow-hidden">
                <div class="card-header bg-dark text-white text-center py-5" style="background: linear-gradient(135deg, #000000 0%, #333333 100%);">
                    <img src="{% static 'images/favicon.svg' %}" alt="Logo" width="64" height="64" class="mb-3">
                    <h2 class="fw-bold mb-1">Únete a Paso</h2>
                    <p class="text-white-50 small mb-0">Lleva tu negocio al siguiente nivel digital.</p>
                </div>

                <div class="card-body p-5">
                    <form method="POST">
                        {% csrf_token %}
                        
                        <h6 class="text-uppercase text-muted fw-bold mb-3 small tracking-wide">
                            <i class="fas fa-user-circle me-1"></i> Tus Datos
                        </h6>
                        <div class="row g-2 mb-3">
                            <div class="col-md-6 form-floating">
                                {{ form.first_name }}
                                <label for="{{ form.first_name.id_for_label }}" class="ps-3">{{ form.first_name.label }}</label>
                            </div>
                            <div class="col-md-6 form-floating">
                                {{ form.last_name }}
                                <label for="{{ form.last_name.id_for_label }}" class="ps-3">{{ form.last_name.label }}</label>
                            </div>
                        </div>

                        <div class="form-floating mb-3">
                            {{ form.email }}
                            <label for="{{ form.email.id_for_label }}">{{ form.email.label }}</label>
                        </div>
                        <div class="form-floating mb-4">
                            {{ form.password }}
                            <label for="{{ form.password.id_for_label }}">{{ form.password.label }}</label>
                            <div class="form-text text-end">Usa al menos 6 caracteres.</div>
                        </div>

                        <h6 class="text-uppercase text-muted fw-bold mb-3 small tracking-wide border-top pt-3">
                            <i class="fas fa-store me-1"></i> Tu Negocio
                        </h6>
                        
                        <div class="form-floating mb-3">
                            {{ form.nombre_negocio }}
                            <label for="{{ form.nombre_negocio.id_for_label }}">{{ form.nombre_negocio.label }}</label>
                        </div>

                        <div class="row g-2 mb-3">
                            <div class="col-md-6 form-floating">
                                {{ form.ciudad }}
                                <label for="{{ form.ciudad.id_for_label }}">{{ form.ciudad.label }}</label>
                            </div>
                            <div class="col-md-6 form-floating">
                                {{ form.direccion }}
                                <label for="{{ form.direccion.id_for_label }}">{{ form.direccion.label }}</label>
                            </div>
                        </div>

                        <div class="input-group mb-3">
                            <span class="input-group-text bg-light border-end-0"><i class="fab fa-whatsapp text-success"></i></span>
                            <div class="form-floating flex-grow-1">
                                {{ form.whatsapp }}
                                <label for="{{ form.whatsapp.id_for_label }}">{{ form.whatsapp.label }}</label>
                            </div>
                        </div>
                        
                        <div class="input-group mb-4">
                            <span class="input-group-text bg-light border-end-0"><i class="fab fa-instagram text-danger"></i></span>
                            <div class="form-floating flex-grow-1">
                                {{ form.instagram }}
                                <label for="{{ form.instagram.id_for_label }}">{{ form.instagram.label }}</label>
                            </div>
                        </div>

                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-dark btn-lg py-3 rounded-3 fw-bold shadow-sm">
                                Crear mi Cuenta Empresarial
                            </button>
                        </div>
                    </form>
                </div>

                <div class="card-footer bg-light text-center py-3">
                    <p class="mb-0 text-muted small">
                        ¿Ya tienes cuenta? <a href="{% url 'saas_login' %}" class="fw-bold text-dark text-decoration-none">Inicia Sesión</a>
                    </p>
                </div>
            </div>
            
            <p class="text-center text-muted mt-4 small">
                <i class="fas fa-lock me-1"></i> Tus datos están protegidos y encriptados.
            </p>
        </div>
    </div>
</div>
{% endblock %}
"""
create_file('templates/registration/register_owner.html', template_content)

# ==============================================================================
# 4. SUBIDA AUTOMÁTICA Y AUTODESTRUCCIÓN
# ==============================================================================
print("🤖 Subiendo cambios a Render...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "UX: Registration form updated to Luxury Level (Cities, Address, Floating Labels)"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ ¡Éxito! El formulario ha sido actualizado.")
except Exception as e:
    print(f"⚠️ Error en git: {e}")

print("💥 Iniciando autodestrucción del script...")
try:
    os.remove(__file__)
    print("✨ Script eliminado. El directorio permanece limpio.")
except Exception as e:
    print(f"⚠️ No pude autodestruirme: {e}")