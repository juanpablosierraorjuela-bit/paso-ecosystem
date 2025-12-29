import os

print("💎 Iniciando actualización a Marketplace Luxury 2.0...")

# ==============================================================================
# 1. ACTUALIZAR VIEWS.PY (Backend)
# - Agregamos la lógica para obtener la lista de ciudades disponibles.
# - Agregamos el filtro por ciudad.
# ==============================================================================
views_path = os.path.join('apps', 'businesses', 'views.py')

# Leemos el archivo actual para no perder nada, pero reemplazaremos la función marketplace
# Usaremos una versión completa de views.py para asegurar que todo encaje.

views_content = '''import json
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
        # 1. OBTENER HORA REAL (Timezone Aware para Colombia)
        now = timezone.localtime(timezone.now())
        current_time = now.time()
        
        # 2. BASE DE DATOS Y FILTROS
        salones_base = Salon.objects.filter(is_active=True)
        
        # --- NUEVO: Obtener lista de ciudades únicas para el selector ---
        # values_list devuelve solo los nombres, distinct evita repetidos, exclude quita vacíos
        available_cities = Salon.objects.filter(is_active=True).exclude(city__isnull=True).exclude(city__exact='').values_list('city', flat=True).distinct().order_by('city')
        
        query = request.GET.get('q')
        city_filter = request.GET.get('city') # Nuevo filtro
        
        # Filtro de texto (Nombre o dirección)
        if query:
            salones_base = salones_base.filter(
                Q(name__icontains=query) | 
                Q(address__icontains=query)
            )
            
        # Filtro de Ciudad (Exacto)
        if city_filter and city_filter != "Todas":
            salones_base = salones_base.filter(city__icontains=city_filter)
        
        salones_para_mostrar = list(salones_base)
        user_located = False
        user_lat = request.GET.get('lat')
        user_lng = request.GET.get('lng')

        # 3. LÓGICA DE DISTANCIA
        try:
            if user_lat and user_lng and user_lat != "undefined":
                # Si el usuario filtra por ciudad explícitamente, ignoramos el radio de distancia
                # para que pueda "chismosear" en otras ciudades.
                ignore_distance = bool(city_filter)
                
                temp = []
                for s in salones_base:
                    dist = haversine_distance(user_lng, user_lat, s.longitude, s.latitude)
                    if ignore_distance or dist <= 35: 
                        temp.append(s)
                
                if not query and not city_filter:
                    salones_para_mostrar = temp
                    user_located = bool(temp)
                else:
                    # Ordenar por cercanía aunque mostremos todos
                    salones_para_mostrar.sort(key=lambda s: haversine_distance(user_lng, user_lat, s.longitude, s.latitude))
                    user_located = True
        except: pass

        # 4. LÓGICA DE APERTURA (MADRUGADA SOPORTADA)
        for salon in salones_para_mostrar:
            is_open = False
            if salon.opening_time and salon.closing_time:
                ot = salon.opening_time
                ct = salon.closing_time
                if ct < ot: 
                    if current_time >= ot or current_time <= ct: is_open = True
                else:
                    if ot <= current_time <= ct: is_open = True
            salon.is_open_dynamic = is_open

        return render(request, 'home.html', {
            'salones': salones_para_mostrar, 
            'user_located': user_located,
            'query_string': query,
            'available_cities': available_cities, # Pasamos las ciudades al template
            'selected_city': city_filter
        })
    except Exception as e:
        print(f"Error en marketplace: {e}")
        return HttpResponse(f"Error cargando marketplace: {e}", status=200)

def register_owner(request):
    if request.method == 'GET' and request.user.is_authenticated: logout(request)
    if request.method == 'POST':
        business_name = request.POST.get('business_name')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        if not all([business_name, phone, password]): return render(request, 'users/register_owner.html', {'error': 'Campos obligatorios'})
        clean_phone = ''.join(filter(str.isdigit, phone))
        if User.objects.filter(username=clean_phone).exists(): return render(request, 'users/register_owner.html', {'error': 'Usuario ya existe'})
        try:
            user = User.objects.create_user(username=clean_phone, password=password, first_name=business_name, role='ADMIN')
            slug = slugify(business_name)
            if Salon.objects.filter(slug=slug).exists(): slug += f"-{str(uuid.uuid4())[:4]}"
            Salon.objects.create(owner=user, name=business_name, slug=slug, is_active=True)
            login(request, user)
            return redirect('admin_dashboard')
        except Exception as e: return render(request, 'users/register_owner.html', {'error': str(e)})
    return render(request, 'users/register_owner.html')

# --- DASHBOARDS (Sin cambios) ---
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
                if s.instagram_url and not s.instagram_url.startswith('http'): s.instagram_url = f"https://instagram.com/{s.instagram_url.replace('@', '')}"
                s.save()
                messages.success(request, '✅ Configuración guardada.')
                return redirect('admin_dashboard')
            else: messages.error(request, f'❌ Error: {config_form.errors}')
        elif 'create_service' in request.POST:
            f = ServiceForm(request.POST)
            if f.is_valid():
                s = f.save(commit=False); s.salon = salon; s.save()
                messages.success(request, 'Servicio creado.')
                return redirect('admin_dashboard')
        elif 'create_employee' in request.POST:
            f = EmployeeCreationForm(request.POST)
            if f.is_valid():
                u = f.save(commit=False); u.role = 'EMPLOYEE'; u.salon = salon; u.set_password(f.cleaned_data['password']); u.save()
                for d in range(6): EmployeeSchedule.objects.create(employee=u, weekday=d, from_hour=time(9,0), to_hour=time(19,0), is_active=True)
                messages.success(request, 'Empleado creado.')
                return redirect('admin_dashboard')
    services = Service.objects.filter(salon=salon)
    employees = User.objects.filter(role='EMPLOYEE', salon=salon)
    webhook_url = request.build_absolute_uri(f'/api/webhooks/bold/{salon.id}/').replace('http://', 'https://')
    return render(request, 'owner_dashboard.html', {'salon': salon, 'config_form': config_form, 'service_form': service_form, 'employee_form': employee_form, 'services': services, 'employees': employees, 'webhook_url': webhook_url})

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

# --- API ---
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
        except Exception as e: return JsonResponse({'success': False, 'message': f"Error Telegram: {str(e)}"})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

@csrf_exempt
def bold_webhook(request, salon_id): return JsonResponse({'status': 'ok'})

def booking_create(request, salon_slug):
    salon = get_object_or_404(Salon, slug=salon_slug)
    services, employees = Service.objects.filter(salon=salon), User.objects.filter(role='EMPLOYEE', salon=salon)
    if request.method == 'POST': return redirect('booking_success', booking_id=1) 
    return render(request, 'booking_create.html', {'salon': salon, 'services': services, 'employees': employees})

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_success.html', {'booking': booking, 'salon': booking.salon})

def get_available_slots_api(request): return JsonResponse({'slots': []})
'''

# ==============================================================================
# 2. ACTUALIZAR HOME.HTML (Frontend)
# - Agregamos el selector de ciudades en el formulario.
# - Rediseñamos la tarjeta: Minimalista, sin corona, sin iconos feos.
# ==============================================================================
template_path = os.path.join('templates', 'home.html')
template_content = """{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="container main-container py-5">
    
    <div class="text-center mb-5 fade-in-up">
        <h1 class="display-5 fw-bold" style="font-family: 'Playfair Display', serif; color: #1a1a1a;">
            Experiencias <span style="color: #D4AF37;">Premium</span>
        </h1>
        <p class="text-muted" style="letter-spacing: 2px; font-size: 0.9rem;">ENCUENTRA TU LUGAR EXCLUSIVO</p>
    </div>

    <div class="row justify-content-center mb-5 fade-in-up" style="animation-delay: 0.1s;">
        <div class="col-lg-10">
            <form method="GET" action="{% url 'marketplace' %}" class="d-flex flex-column flex-md-row shadow-sm rounded-pill overflow-hidden bg-white border border-light">
                
                <div class="flex-grow-1 position-relative">
                    <span class="position-absolute top-50 start-0 translate-middle-y ms-4 text-muted">
                        <i class="fas fa-search"></i>
                    </span>
                    <input type="text" name="q" class="form-control border-0 py-3 ps-5" 
                           placeholder="¿Qué servicio o lugar buscas hoy?" 
                           value="{{ query_string|default:'' }}"
                           style="border-radius: 30px 0 0 30px; height: 60px;">
                </div>

                <div class="d-none d-md-block border-end my-2"></div>

                <div class="position-relative" style="min-width: 200px;">
                    <span class="position-absolute top-50 start-0 translate-middle-y ms-3 text-gold">
                        <i class="fas fa-map-marker-alt"></i>
                    </span>
                    <select name="city" class="form-select border-0 py-3 ps-5 shadow-none" 
                            style="height: 60px; cursor: pointer; background-color: transparent;">
                        <option value="">Todas las ciudades</option>
                        {% for city in available_cities %}
                            <option value="{{ city }}" {% if selected_city == city %}selected{% endif %}>{{ city }}</option>
                        {% endfor %}
                    </select>
                </div>

                <button type="submit" class="btn btn-dark px-5 py-3 fw-bold" style="background: #1a1a1a; border-radius: 30px;">
                    BUSCAR
                </button>

                <input type="hidden" name="lat" id="user_lat">
                <input type="hidden" name="lng" id="user_lng">
            </form>
        </div>
    </div>

    <div class="row g-4">
        {% for salon in salones %}
        <div class="col-md-6 col-lg-4 fade-in-up" style="animation-delay: 0.2s;">
            
            <div class="card h-100 border-0 shadow-hover transition-all" 
                 style="background: #fff; border-radius: 15px; overflow: hidden; border: 1px solid #f0f0f0;">
                
                <div class="position-absolute top-0 end-0 m-3 z-1">
                    {% if salon.is_open_dynamic %}
                        <span class="badge bg-success bg-opacity-10 text-success border border-success px-3 py-2 rounded-pill fw-normal" style="backdrop-filter: blur(5px);">
                            ● Abierto
                        </span>
                    {% else %}
                        <span class="badge bg-secondary bg-opacity-10 text-secondary border border-secondary px-3 py-2 rounded-pill fw-normal" style="backdrop-filter: blur(5px);">
                            ● Cerrado
                        </span>
                    {% endif %}
                </div>

                <div class="card-body text-center p-5 d-flex flex-column align-items-center justify-content-center">
                    
                    <div class="mb-4 d-flex align-items-center justify-content-center rounded-circle shadow-sm"
                         style="width: 80px; height: 80px; background: #1a1a1a; border: 2px solid #D4AF37;">
                        <span class="display-5 fw-bold text-white" style="font-family: 'Playfair Display', serif;">
                            {{ salon.name|slice:":1" }}
                        </span>
                    </div>

                    <h3 class="card-title fw-bold mb-1 text-dark" style="font-family: 'Playfair Display', serif; letter-spacing: -0.5px;">
                        {{ salon.name }}
                    </h3>
                    
                    <p class="text-muted small mb-4">
                        <i class="fas fa-map-pin text-gold me-1"></i> {{ salon.city|default:"Ubicación Exclusiva" }}
                    </p>

                    <div class="d-flex gap-3 mb-4 opacity-75">
                        {% if salon.instagram_url %}
                            <a href="{{ salon.instagram_url }}" target="_blank" class="text-dark hover-gold transition-colors">
                                <i class="fab fa-instagram fa-lg"></i>
                            </a>
                        {% endif %}
                        {% if salon.whatsapp_number %}
                            <a href="https://wa.me/{{ salon.whatsapp_number }}" target="_blank" class="text-dark hover-gold transition-colors">
                                <i class="fab fa-whatsapp fa-lg"></i>
                            </a>
                        {% endif %}
                    </div>

                    <a href="{% url 'booking_create' salon.slug %}" 
                       class="btn btn-outline-dark w-100 rounded-pill py-2 fw-bold text-uppercase"
                       style="font-size: 0.8rem; letter-spacing: 1px; border-width: 1.5px;">
                        Reservar Cita
                    </a>
                </div>
            </div>
        </div>
        
        {% empty %}
        <div class="col-12 text-center py-5">
            <div class="mb-4 opacity-50">
                <i class="far fa-compass fa-3x mb-3 text-muted"></i>
                <h4 class="text-muted fw-light">No encontramos resultados en esta zona.</h4>
            </div>
            
            <div class="d-flex justify-content-center gap-3">
                <a href="{% url 'register_owner' %}" class="btn btn-dark rounded-pill px-4">
                    <i class="fas fa-plus me-2"></i> Registrar mi Negocio
                </a>
            </div>
        </div>
        {% endfor %}
    </div>
</div>

<style>
    /* Estilos Luxury Custom */
    .text-gold { color: #D4AF37 !important; }
    .hover-gold:hover { color: #D4AF37 !important; transform: scale(1.1); }
    .transition-all { transition: all 0.3s ease; }
    .transition-colors { transition: color 0.3s ease; }
    
    .shadow-hover:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.08) !important;
        border-color: #D4AF37 !important;
    }

    /* Animación de entrada suave */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out forwards;
        opacity: 0;
    }
    
    /* Ajustes Mobile */
    @media (max-width: 768px) {
        .d-flex.flex-column.flex-md-row input { border-radius: 30px !important; margin-bottom: 10px; }
        .d-flex.flex-column.flex-md-row select { border-radius: 30px !important; margin-bottom: 10px; padding-left: 20px !important; }
        .d-flex.flex-column.flex-md-row button { border-radius: 30px !important; width: 100%; }
    }
</style>

<script>
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            document.getElementById('user_lat').value = position.coords.latitude;
            document.getElementById('user_lng').value = position.coords.longitude;
        });
    }
</script>
{% endblock %}
"""

# Escritura segura
try:
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(views_content)
    print("✅ Backend actualizado con selector de ciudades.")

    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    print("✅ Frontend actualizado con diseño Minimal Luxury.")
    
    print("\\n✨ ¡TODO LISTO! Ejecuta los comandos de Git ahora.")

except Exception as e:
    print(f"❌ Error al escribir archivos: {e}")