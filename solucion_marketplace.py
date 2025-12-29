import os
import sys

# --- 1. NUEVO DISEÑO DE LUJO PARA EL MARKETPLACE (home.html) ---
# Este HTML incluye estilos CSS dorados, tarjetas elegantes y la lógica de etiquetas
nuevo_home_html = """
{% extends 'base_saas.html' %}
{% load static %}

{% block title %}Marketplace | Ecosistema PASO{% endblock %}

{% block content %}
<style>
    /* ESTILOS LUXURY PASO */
    :root {
        --paso-gold: #D4AF37;
        --paso-black: #1a1a1a;
        --paso-gray: #f8f9fa;
    }
    
    body {
        background-color: #fcfcfc;
    }

    .hero-section {
        background: linear-gradient(135deg, var(--paso-black) 0%, #333 100%);
        color: white;
        padding: 4rem 0 6rem;
        margin-bottom: -3rem;
        border-radius: 0 0 50% 50% / 4%;
    }

    .search-box {
        background: white;
        padding: 1.5rem;
        border-radius: 50px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transform: translateY(-20px);
    }

    .search-input {
        border: none;
        font-size: 1.1rem;
        padding: 0.5rem 1.5rem;
    }
    
    .search-input:focus {
        box-shadow: none;
        outline: none;
    }

    .btn-search {
        background-color: var(--paso-black);
        color: var(--paso-gold);
        border-radius: 30px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .btn-search:hover {
        background-color: var(--paso-gold);
        color: var(--paso-black);
        transform: translateY(-2px);
    }

    /* TARJETA DE NEGOCIO LUXURY */
    .salon-card {
        background: white;
        border: none;
        border-radius: 15px;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        height: 100%;
        position: relative;
    }

    .salon-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(212, 175, 55, 0.15); /* Sombra dorada suave */
    }

    .salon-img-wrapper {
        height: 200px;
        overflow: hidden;
        position: relative;
        background-color: #f0f0f0;
    }

    .salon-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
    }

    .salon-card:hover .salon-img {
        transform: scale(1.05);
    }

    .status-badge {
        position: absolute;
        top: 15px;
        right: 15px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        z-index: 2;
    }

    .status-open {
        background-color: #ffffff;
        color: #198754;
        border: 2px solid #198754;
    }

    .status-closed {
        background-color: #ffffff;
        color: #dc3545;
        border: 2px solid #dc3545;
    }

    .card-body {
        padding: 1.5rem;
    }

    .salon-name {
        font-family: 'Playfair Display', serif; /* Fuente elegante */
        font-weight: 700;
        font-size: 1.25rem;
        color: var(--paso-black);
        margin-bottom: 0.5rem;
    }

    .salon-location {
        color: #6c757d;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 5px;
        margin-bottom: 1rem;
    }

    .btn-book {
        width: 100%;
        background: transparent;
        color: var(--paso-black);
        border: 1px solid var(--paso-black);
        padding: 0.6rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .btn-book:hover {
        background: var(--paso-black);
        color: var(--paso-gold);
        border-color: var(--paso-black);
    }

    .no-results {
        text-align: center;
        padding: 4rem;
        color: #6c757d;
    }
</style>

<div class="hero-section text-center">
    <div class="container">
        <h1 class="display-4 fw-bold mb-3">Encuentra tu estilo</h1>
        <p class="lead mb-4 opacity-75">Los mejores profesionales de belleza en un solo lugar</p>
    </div>
</div>

<div class="container mb-5" style="margin-top: -3rem;">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <form method="get" class="search-box d-flex gap-2">
                <input type="text" name="q" class="form-control search-input" placeholder="¿Qué buscas? (Ej: Barbería, Uñas, Centro)" value="{{ request.GET.q }}">
                <button type="submit" class="btn btn-search">
                    <i class="fas fa-search me-2"></i> Buscar
                </button>
            </form>
        </div>
    </div>
</div>

<div class="container py-4">
    <div class="row g-4">
        {% for salon in salones %}
        <div class="col-md-6 col-lg-4">
            <div class="salon-card h-100">
                
                <div class="salon-img-wrapper">
                    {% if salon.logo %}
                        <img src="{{ salon.logo.url }}" alt="{{ salon.name }}" class="salon-img">
                    {% else %}
                        <div class="d-flex align-items-center justify-content-center h-100 bg-dark text-white">
                            <i class="fas fa-store fa-3x text-warning"></i>
                        </div>
                    {% endif %}

                    {% if salon.is_open_now_dynamic %}
                        <span class="status-badge status-open">
                            <i class="fas fa-circle fa-xs me-1"></i> Abierto
                        </span>
                    {% else %}
                        <span class="status-badge status-closed">
                            <i class="fas fa-clock fa-xs me-1"></i> Cerrado
                        </span>
                    {% endif %}
                </div>

                <div class="card-body">
                    <h3 class="salon-name">{{ salon.name }}</h3>
                    <div class="salon-location">
                        <i class="fas fa-map-marker-alt text-warning"></i>
                        <span>{{ salon.address|default:"Sin dirección" }}, {{ salon.city|default:"Tunja" }}</span>
                    </div>
                    
                    <a href="{% url 'booking_create' salon.slug %}" class="btn btn-book">
                        Reservar Cita
                    </a>
                </div>
            </div>
        </div>
        {% empty %}
        <div class="col-12 no-results">
            <i class="fas fa-search fa-3x mb-3 text-muted"></i>
            <h3>No encontramos negocios con esa búsqueda</h3>
            <p>Intenta con otra palabra clave o explora todos los negocios.</p>
            <a href="{% url 'marketplace' %}" class="btn btn-link text-dark">Ver todos</a>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

# --- 2. LOGICA ROBUSTA PARA VIEWS.PY (Marketplace) ---
# Mantiene todas las vistas existentes pero pule la lógica de horarios
nuevo_views_py = """import json
from decimal import Decimal
import uuid
import hashlib
from urllib import request as url_request, parse, error
from datetime import datetime, time, date
from math import radians, cos, sin, asin, sqrt

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from django.db.models import Q

from .models import Salon, Service, Booking, EmployeeSchedule
from .forms import SalonIntegrationsForm, ServiceForm, EmployeeCreationForm, ScheduleForm

User = get_user_model()

# --- UTILIDADES ---
def haversine_distance(lon1, lat1, lon2, lat2):
    try:
        if any(x in [None, ''] for x in [lon1, lat1, lon2, lat2]): return float('inf')
        lon1, lat1, lon2, lat2 = map(float, [str(lon1).replace(',', '.'), str(lat1).replace(',', '.'), str(lon2).replace(',', '.'), str(lat2).replace(',', '.')])
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        a = sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2
        return 2 * asin(sqrt(a)) * 6371 
    except: return float('inf')

# --- VISTAS PÚBLICAS ---
def logout_view(request):
    logout(request)
    return redirect('home')

def home(request):
    return render(request, 'home_landing.html')

def marketplace(request):
    try:
        # 1. Obtener la hora actual en COLOMBIA (Importante para que coincida con el usuario)
        now = timezone.localtime(timezone.now())
        current_weekday = now.weekday() # 0=Lunes, 6=Domingo
        current_time = now.time()

        # 2. Filtrar salones activos
        salones_base = Salon.objects.filter(is_active=True)
        query = request.GET.get('q')
        
        if query:
            salones_base = salones_base.filter(
                Q(name__icontains=query) | 
                Q(city__icontains=query) | 
                Q(address__icontains=query)
            )
        
        salones_para_mostrar = list(salones_base)
        user_located = False
        user_lat = request.GET.get('lat')
        user_lng = request.GET.get('lng')

        # 3. Lógica de Distancia (Si el usuario da permisos)
        try:
            if user_lat and user_lng and user_lat != "undefined":
                temp = []
                for s in salones_base:
                    dist = haversine_distance(user_lng, user_lat, s.longitude, s.latitude)
                    if dist <= 35: temp.append(s)
                
                if not query:
                    salones_para_mostrar = temp
                    user_located = bool(temp)
                else:
                    salones_para_mostrar.sort(key=lambda s: haversine_distance(user_lng, user_lat, s.longitude, s.latitude))
                    user_located = True
        except: pass

        # 4. LOGICA MAESTRA DE APERTURA (El Script Mágico)
        # Verifica si AL MENOS UN empleado está trabajando AHORA MISMO
        for salon in salones_para_mostrar:
            try:
                # Buscamos horarios activos para hoy, que cubran la hora actual
                is_open = EmployeeSchedule.objects.filter(
                    employee__salon=salon,          # De este salón
                    employee__role='EMPLOYEE',      # Que sea empleado/barbero
                    is_active=True,                 # Que el horario esté activo
                    weekday=current_weekday,        # Que sea hoy
                    from_hour__lte=current_time,    # Que haya abierto antes de ahora
                    to_hour__gte=current_time       # Que cierre después de ahora
                ).exists()
                
                salon.is_open_now_dynamic = is_open
            except Exception as e:
                print(f"Error calculando horario para {salon.slug}: {e}")
                salon.is_open_now_dynamic = False

        return render(request, 'home.html', {'salones': salones_para_mostrar, 'user_located': user_located})
    except Exception as e:
        return HttpResponse(f"Error cargando marketplace: {e}", status=200)

def register_owner(request):
    if request.method == 'GET' and request.user.is_authenticated: logout(request)
    if request.method == 'POST':
        business_name = request.POST.get('business_name')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        if not all([business_name, phone, password]): return render(request, 'users/register_owner.html', {'error': 'Campos obligatorios'})

        clean_phone = ''.join(filter(str.isdigit, phone))
        if User.objects.filter(username=clean_phone).exists():
            return render(request, 'users/register_owner.html', {'error': 'Usuario ya existe'})

        try:
            user = User.objects.create_user(username=clean_phone, password=password, first_name=business_name, role='ADMIN')
            slug = slugify(business_name)
            if Salon.objects.filter(slug=slug).exists(): slug += f"-{str(uuid.uuid4())[:4]}"
            Salon.objects.create(owner=user, name=business_name, slug=slug, is_active=True)
            login(request, user)
            return redirect('admin_dashboard')
        except Exception as e:
            return render(request, 'users/register_owner.html', {'error': str(e)})

    return render(request, 'users/register_owner.html')

# --- DASHBOARDS ---
@login_required
def owner_dashboard(request):
    salon = Salon.objects.filter(owner=request.user).first()
    if not salon: return redirect('home')

    config_form = SalonIntegrationsForm(instance=salon)
    service_form = ServiceForm()
    employee_form = EmployeeCreationForm()

    if request.method == 'POST':
        if 'update_config' in request.POST:
            config_form = SalonIntegrationsForm(request.POST, request.FILES, instance=salon)
            if config_form.is_valid():
                s = config_form.save(commit=False)
                if s.instagram_url and not s.instagram_url.startswith('http'):
                    s.instagram_url = f"https://instagram.com/{s.instagram_url.replace('@', '')}"
                s.save()
                messages.success(request, '✅ Configuración guardada.')
                return redirect('admin_dashboard')
            else:
                messages.error(request, f'❌ Error: {config_form.errors}')
        
        elif 'create_service' in request.POST:
            f = ServiceForm(request.POST)
            if f.is_valid():
                s = f.save(commit=False)
                s.salon = salon
                s.save()
                messages.success(request, 'Servicio creado.')
                return redirect('admin_dashboard')

        elif 'create_employee' in request.POST:
            f = EmployeeCreationForm(request.POST)
            if f.is_valid():
                u = f.save(commit=False)
                u.role = 'EMPLOYEE'
                u.salon = salon
                u.set_password(f.cleaned_data['password'])
                u.save()
                # Crear horario base (Lunes a Sábado 9am-7pm)
                for d in range(6):
                    EmployeeSchedule.objects.create(employee=u, weekday=d, from_hour=time(9,0), to_hour=time(19,0), is_active=True)
                messages.success(request, 'Empleado creado.')
                return redirect('admin_dashboard')

    services = Service.objects.filter(salon=salon)
    employees = User.objects.filter(role='EMPLOYEE', salon=salon)
    
    webhook_url = request.build_absolute_uri(f'/api/webhooks/bold/{salon.id}/').replace('http://', 'https://')
    
    return render(request, 'owner_dashboard.html', {
        'salon': salon, 'config_form': config_form, 'service_form': service_form,
        'employee_form': employee_form, 'services': services, 'employees': employees,
        'webhook_url': webhook_url
    })

@login_required
def dashboard(request):
    user = request.user
    if getattr(user, 'role', '') == 'ADMIN': return redirect('admin_dashboard')
    if getattr(user, 'role', '') == 'EMPLOYEE': return redirect('employee_panel')
    citas = Booking.objects.filter(customer=user).order_by('-start_time')
    return render(request, 'dashboard.html', {'citas': citas})

@login_required
def employee_dashboard(request):
    if 'delete_id' in request.POST:
        EmployeeSchedule.objects.filter(id=request.POST.get('delete_id'), employee=request.user).delete()
        return redirect('employee_panel')
    form = ScheduleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        s = form.save(commit=False); s.employee = request.user; s.save()
        return redirect('employee_panel')
    schedules = EmployeeSchedule.objects.filter(employee=request.user).order_by('weekday', 'from_hour')
    return render(request, 'employee_dashboard.html', {'schedules': schedules, 'form': form})

@login_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if service.salon.owner == request.user: service.delete()
    return redirect('admin_dashboard')

# --- API Y WEBHOOKS ---
@login_required
def test_telegram_integration(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token, chat_id = data.get('token'), data.get('chat_id')
            if not token or not chat_id: return JsonResponse({'success': False, 'message': 'Faltan datos'})
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {'chat_id': chat_id, 'text': "✅ ¡Conexión Exitosa con PASO Ecosistema!"}
            
            req = url_request.Request(url, data=parse.urlencode(payload).encode())
            url_request.urlopen(req, timeout=5) 
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Error Telegram: {str(e)}"})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@csrf_exempt
def bold_webhook(request, salon_id):
    return JsonResponse({'status': 'ok'})

def booking_create(request, salon_slug):
    salon = get_object_or_404(Salon, slug=salon_slug)
    services, employees = Service.objects.filter(salon=salon), User.objects.filter(role='EMPLOYEE', salon=salon)
    if request.method == 'POST': return redirect('booking_success', booking_id=1) 
    return render(request, 'booking_create.html', {'salon': salon, 'services': services, 'employees': employees})

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_success.html', {'booking': booking, 'salon': booking.salon})

def get_available_slots_api(request):
    return JsonResponse({'slots': []})
"""

# --- EJECUCIÓN: ESCRIBIR ARCHIVOS ---

# 1. Actualizar el diseño (home.html)
path_html = os.path.join('templates', 'home.html')
try:
    with open(path_html, 'w', encoding='utf-8') as f:
        f.write(nuevo_home_html)
    print("✅ Diseño del Marketplace actualizado con estilo Luxury.")
except Exception as e:
    print(f"❌ Error escribiendo home.html: {e}")

# 2. Actualizar la lógica (views.py)
path_views = os.path.join('apps', 'businesses', 'views.py')
try:
    with open(path_views, 'w', encoding='utf-8') as f:
        f.write(nuevo_views_py)
    print("✅ Lógica de horarios actualizada correctamente.")
except Exception as e:
    print(f"❌ Error escribiendo views.py: {e}")

print("\\n✨ SCRIPT TERMINADO: Sube los cambios a GitHub para ver la magia.")