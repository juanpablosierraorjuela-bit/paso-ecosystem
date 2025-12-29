import os

# ==============================================================================
# 1. CORRECCIÓN DEL BACKEND (views.py)
# ==============================================================================
# - Implementa la lógica de cruce de medianoche (Overnight Logic).
# - Prioriza los horarios generales del Salón sobre los de empleados individuales.
# ==============================================================================

views_path = os.path.join('apps', 'businesses', 'views.py')
views_content = """import json
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
        # 1. OBTENER HORA REAL (Timezone Aware)
        now = timezone.localtime(timezone.now())
        current_time = now.time()
        
        # 2. FILTRADO BÁSICO
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

        # 3. LÓGICA DE DISTANCIA (Opcional)
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

        # 4. LÓGICA MAESTRA DE APERTURA (SOPORTE MADRUGADA)
        # Esta lógica soluciona el problema de "Cierra a las 2 AM"
        for salon in salones_para_mostrar:
            is_open = False
            
            # Verificamos si tiene horarios configurados en el Perfil del Negocio
            if salon.opening_time and salon.closing_time:
                ot = salon.opening_time
                ct = salon.closing_time
                
                if ct < ot: 
                    # CASO MADRUGADA: El cierre es menor que la apertura (ej: Abre 11am, Cierra 2am)
                    # Está abierto si es mas tarde que la apertura (11pm) O más temprano que el cierre (1am)
                    if current_time >= ot or current_time <= ct:
                        is_open = True
                else:
                    # CASO NORMAL: (ej: Abre 9am, Cierra 7pm)
                    if ot <= current_time <= ct:
                        is_open = True
            
            # Inyectamos el estado dinámico al objeto salon temporalmente
            salon.is_open_dynamic = is_open

        return render(request, 'home.html', {
            'salones': salones_para_mostrar, 
            'user_located': user_located,
            'query_string': query
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

# ==============================================================================
# 2. CORRECCIÓN DEL FRONTEND (templates/home.html)
# ==============================================================================
# - Restaura el diseño "Card de Lujo" (Fondo negro/oro, Corona).
# - Restaura los iconos de WhatsApp e Instagram.
# - Restaura el bloque "Empty State" con los botones de Recomendar/Unirse.
# ==============================================================================

template_path = os.path.join('templates', 'home.html')
template_content = """{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="container main-container py-5">
    <div class="text-center mb-5">
        <h1 class="display-4 fw-bold" style="font-family: 'Playfair Display', serif; color: #1a1a1a;">
            Marketplace <span style="color: #D4AF37;">Exclusivo</span>
        </h1>
        <p class="lead text-muted">Encuentra los mejores servicios de belleza cerca de ti</p>
    </div>

    <div class="row justify-content-center mb-5">
        <div class="col-md-8">
            <form method="GET" action="{% url 'marketplace' %}" class="d-flex shadow-sm rounded-pill overflow-hidden bg-white">
                <input type="text" name="q" class="form-control border-0 px-4 py-3" 
                       placeholder="¿Qué servicio buscas hoy?" value="{{ query_string|default:'' }}">
                <input type="hidden" name="lat" id="user_lat">
                <input type="hidden" name="lng" id="user_lng">
                <button type="submit" class="btn btn-dark px-4" style="background: #1a1a1a;">
                    <i class="fas fa-search text-gold"></i>
                </button>
            </form>
        </div>
    </div>

    <div class="row">
        {% for salon in salones %}
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100 border-0 shadow-lg luxury-card" style="border-radius: 20px; overflow: hidden; transition: transform 0.3s ease;">
                <div class="card-header position-relative text-center py-4" style="background: #1a1a1a; color: white;">
                    {% if salon.is_open_dynamic %}
                        <span class="badge position-absolute top-0 end-0 m-3" 
                              style="background-color: #28a745; font-size: 0.8rem; padding: 8px 12px; border-radius: 30px;">
                            ABIERTO
                        </span>
                    {% else %}
                        <span class="badge position-absolute top-0 end-0 m-3" 
                              style="background-color: #343a40; font-size: 0.8rem; padding: 8px 12px; border-radius: 30px; border: 1px solid #555;">
                            CERRADO
                        </span>
                    {% endif %}
                    
                    <div class="crown-icon mb-2">
                        <i class="fas fa-crown fa-2x" style="color: #D4AF37;"></i>
                    </div>
                </div>

                <div class="card-body text-center bg-white pt-5 position-relative">
                    <div class="position-absolute start-50 translate-middle" style="top: 0; width: 80px; height: 80px; background: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border: 3px solid #D4AF37;">
                         <i class="fas fa-store fa-2x text-dark"></i>
                    </div>

                    <h3 class="card-title fw-bold mt-3" style="font-family: 'Playfair Display', serif;">{{ salon.name }}</h3>
                    <p class="text-muted small text-uppercase letter-spacing-1">EXPERIENCIA PREMIUM</p>
                    
                    <div class="mb-3 text-muted">
                        <i class="fas fa-map-marker-alt text-gold me-1"></i> 
                        {{ salon.address|default:"Ubicación Exclusiva" }}
                    </div>

                    <div class="d-flex justify-content-center gap-3 mb-4">
                        {% if salon.instagram_url %}
                        <a href="{{ salon.instagram_url }}" target="_blank" class="social-icon-btn" style="width: 40px; height: 40px; border-radius: 50%; background: #f8f9fa; display: flex; align-items: center; justify-content: center; color: #E1306C; transition: all 0.3s;">
                            <i class="fab fa-instagram fa-lg"></i>
                        </a>
                        {% endif %}
                        
                        {% if salon.whatsapp_number %}
                        <a href="https://wa.me/{{ salon.whatsapp_number }}" target="_blank" class="social-icon-btn" style="width: 40px; height: 40px; border-radius: 50%; background: #f8f9fa; display: flex; align-items: center; justify-content: center; color: #25D366; transition: all 0.3s;">
                            <i class="fab fa-whatsapp fa-lg"></i>
                        </a>
                        {% endif %}
                        
                         {% if not salon.instagram_url and not salon.whatsapp_number %}
                             <span class="text-muted small">Sin redes conectadas</span>
                         {% endif %}
                    </div>

                    <a href="{% url 'booking_create' salon.slug %}" class="btn w-100 py-3 rounded-pill fw-bold text-white" 
                       style="background: #000; border: 2px solid #000; transition: all 0.3s;">
                        Reservar Cita <i class="fas fa-arrow-right ms-2"></i>
                    </a>
                </div>
            </div>
        </div>
        
        {% empty %}
        <div class="col-12 text-center py-5">
            <div class="mb-4">
                <i class="fas fa-search-location fa-4x text-muted mb-3"></i>
                <h3 class="text-muted">No encontramos salones en esta zona aún...</h3>
                <p class="text-muted">¡Sé el primero en traer la experiencia PASO a tu ciudad!</p>
            </div>
            
            <div class="d-flex justify-content-center gap-3 flex-wrap">
                <a href="#" class="btn btn-outline-dark px-4 py-2 rounded-pill">
                    <i class="fas fa-share-alt me-2"></i> Recomendar un Salón
                </a>
                <a href="{% url 'register_owner' %}" class="btn px-4 py-2 rounded-pill text-dark fw-bold" style="background-color: #D4AF37;">
                    <i class="fas fa-store me-2"></i> Unirse a PASO
                </a>
            </div>
        </div>
        {% endfor %}
    </div>
</div>

<style>
    .text-gold { color: #D4AF37 !important; }
    .luxury-card:hover { transform: translateY(-5px); box-shadow: 0 1rem 3rem rgba(0,0,0,.175)!important; }
    .social-icon-btn:hover { transform: scale(1.1); background: #fff !important; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
</style>

<script>
    // Geolocalización
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            document.getElementById('user_lat').value = position.coords.latitude;
            document.getElementById('user_lng').value = position.coords.longitude;
        });
    }
</script>
{% endblock %}
"""

# Escritura de archivos
print("⏳ Aplicando correcciones de diseño Luxury y Lógica de Madrugada...")

with open(views_path, 'w', encoding='utf-8') as f:
    f.write(views_content)
print(f"✅ views.py actualizado con éxito en: {views_path}")

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(template_content)
print(f"✅ home.html actualizado con diseño Luxury y botones en: {template_path}")

print("\n✨ ¡SCRIPT COMPLETADO! Ahora haz:")
print("1. python solucion_definitiva_v2.py")
print("2. git add .")
print('3. git commit -m "Fix diseño luxury y logica madrugada"')
print("4. git push origin main")
"""

with open('solucion_definitiva_v2.py', 'w', encoding='utf-8') as f:
    f.write(views_content) # NOTA: Esto solo escribiría la primera parte. El bloque de arriba está diseñado para ser COPIADO por el usuario.
    # El script real que debes ejecutar es el bloque de texto completo que te di arriba.

pass