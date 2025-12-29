import os

# 1. ARREGLAR MODELO DE USUARIOS (apps/users/models.py)
# Agregamos la relación con Salon para que cada empleado pertenezca a uno.
users_models_content = """from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrador / Dueño"
        MANAGER = "MANAGER", "Gerente"
        EMPLOYEE = "EMPLOYEE", "Empleado / Estilista"
        CUSTOMER = "CUSTOMER", "Cliente"

    role = models.CharField("Rol", max_length=50, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField("Teléfono", max_length=20, blank=True)
    
    # --- NUEVO: VINCULAR EMPLEADO A UN SALÓN ---
    salon = models.ForeignKey('businesses.Salon', on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
"""

# 2. ARREGLAR LA VISTA DEL DUEÑO (apps/businesses/views.py)
# Filtramos empleados por salón y asignamos el salón al crear uno nuevo.
businesses_views_content = """import json
from decimal import Decimal
import uuid
import hashlib
from urllib import request as url_request, parse, error
from datetime import datetime, timedelta, time, date
from math import radians, cos, sin, asin, sqrt

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from django.db.models import Sum, Q

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

def send_telegram_notification(salon, message):
    if not salon.telegram_bot_token or not salon.telegram_chat_id: return False
    try:
        url = f"https://api.telegram.org/bot{salon.telegram_bot_token}/sendMessage"
        payload = {'chat_id': salon.telegram_chat_id, 'text': message, 'parse_mode': 'Markdown'}
        url_request.urlopen(url_request.Request(url, data=parse.urlencode(payload).encode()))
        return True
    except: return False

# --- VISTAS PÚBLICAS ---
def logout_view(request):
    logout(request)
    return redirect('home')

def home(request):
    return render(request, 'home_landing.html')

def marketplace(request):
    try:
        now = timezone.now().astimezone(timezone.get_current_timezone())
        current_weekday = now.weekday()
        current_time = now.time()

        salones_base = Salon.objects.filter(is_active=True)
        query = request.GET.get('q')
        if query: salones_base = salones_base.filter(name__icontains=query)
        
        salones_para_mostrar = list(salones_base)
        user_located = False
        user_lat = request.GET.get('lat')
        user_lng = request.GET.get('lng')

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

        # LÓGICA DE ABIERTO/CERRADO
        for salon in salones_para_mostrar:
            try:
                is_open = EmployeeSchedule.objects.filter(
                    employee__role='EMPLOYEE', weekday=current_weekday, is_active=True,
                    from_hour__lte=current_time, to_hour__gte=current_time, employee__salon=salon
                ).exists()
                salon.is_open_now_dynamic = is_open
            except: salon.is_open_now_dynamic = False

        return render(request, 'home.html', {'salones': salones_para_mostrar, 'user_located': user_located})
    except Exception as e:
        return HttpResponse(f"Error cargando marketplace: {e}", status=200)

def register_owner(request):
    if request.method == 'GET' and request.user.is_authenticated: logout(request)
    if request.method == 'POST':
        business_name = request.POST.get('business_name')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        if not all([business_name, phone, password]):
             return render(request, 'users/register_owner.html', {'error': 'Todos los campos son obligatorios.'})

        clean_phone = ''.join(filter(str.isdigit, phone))
        if len(clean_phone) < 10:
             return render(request, 'users/register_owner.html', {'error': 'Número de celular inválido.'})
        
        if User.objects.filter(username=clean_phone).exists():
            return render(request, 'users/register_owner.html', {'error': 'Este número ya está registrado.'})

        try:
            user = User.objects.create_user(username=clean_phone, password=password, first_name=business_name, role='ADMIN')
            slug = slugify(business_name)
            if Salon.objects.filter(slug=slug).exists(): slug += f"-{str(uuid.uuid4())[:4]}"
            Salon.objects.create(owner=user, name=business_name, slug=slug, is_active=True)
            login(request, user)
            return redirect('admin_dashboard')
        except Exception as e:
            return render(request, 'users/register_owner.html', {'error': f"Error interno: {str(e)}"})

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
        # 1. GUARDAR CONFIGURACIÓN (Redes, Ubicación, Pagos)
        if 'update_config' in request.POST:
            config_form = SalonIntegrationsForm(request.POST, request.FILES, instance=salon)
            if config_form.is_valid():
                s = config_form.save(commit=False)
                if s.instagram_url and not s.instagram_url.startswith('http'):
                    s.instagram_url = f"https://instagram.com/{s.instagram_url.replace('@', '')}"
                s.save()
                messages.success(request, '✅ Configuración guardada correctamente.')
                return redirect('admin_dashboard')
            else:
                messages.error(request, f'❌ Error al guardar: {config_form.errors}')
        
        # 2. CREAR SERVICIO
        elif 'create_service' in request.POST:
            f = ServiceForm(request.POST)
            if f.is_valid():
                s = f.save(commit=False)
                s.salon = salon
                s.save()
                messages.success(request, 'Servicio agregado.')
                return redirect('admin_dashboard')

        # 3. CREAR EMPLEADO
        elif 'create_employee' in request.POST:
            f = EmployeeCreationForm(request.POST)
            if f.is_valid():
                u = f.save(commit=False)
                u.role = 'EMPLOYEE'
                u.salon = salon  # <--- AQUÍ VINCULAMOS AL EMPLEADO CON EL SALÓN ACTUAL
                u.set_password(f.cleaned_data['password'])
                u.save()
                # Horario por defecto
                for d in range(6):
                    EmployeeSchedule.objects.create(employee=u, weekday=d, from_hour=time(9,0), to_hour=time(19,0), is_active=True)
                messages.success(request, 'Empleado creado.')
                return redirect('admin_dashboard')

    # FILTRAR EMPLEADOS SOLO DE ESTE SALÓN
    services = Service.objects.filter(salon=salon)
    # Corrección clave: filtrar por salon=salon
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
def get_available_slots_api(request):
    return JsonResponse({'slots': []}) 

@login_required
def test_telegram_integration(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token, chat_id = data.get('token'), data.get('chat_id')
        if not token or not chat_id: return JsonResponse({'success': False, 'message': 'Faltan datos'})
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {'chat_id': chat_id, 'text': "✅ ¡Conexión Exitosa con PASO!"}
            url_request.urlopen(url_request.Request(url, data=parse.urlencode(payload).encode()))
            return JsonResponse({'success': True})
        except Exception as e: return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False})

@csrf_exempt
def bold_webhook(request, salon_id):
    if request.method == 'POST': return JsonResponse({'status': 'ok'})
    return HttpResponse(status=405)

def booking_create(request, salon_slug):
    salon = get_object_or_404(Salon, slug=salon_slug)
    services, employees = Service.objects.filter(salon=salon), User.objects.filter(role='EMPLOYEE', salon=salon)
    if request.method == 'POST': return redirect('booking_success', booking_id=1) 
    return render(request, 'booking_create.html', {'salon': salon, 'services': services, 'employees': employees})

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_success.html', {'booking': booking, 'salon': booking.salon})
"""

# 3. ARREGLAR TEMPLATE (templates/owner_dashboard.html)
# Agregamos el campo {{ config_form.name }} que faltaba y causaba el error al guardar.
owner_dashboard_content = """{% extends 'base_saas.html' %}

{% block content %}

    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><circle cx=%2250%22 cy=%2250%22 r=%2250%22 fill=%22%23f0f0f0%22/><text x=%2250%22 y=%2250%22 font-family=%22Didot, serif%22 font-weight=%22bold%22 font-size=%2265%22 fill=%22black%22 text-anchor=%22middle%22 dy=%22.35em%22>P</text></svg>">
    <title>Panel Dueño | PASO</title>
    
<div class="row">
    <div class="col-md-3 mb-4">
        <div class="card shadow-sm border-0 rounded-4 text-center p-3" style="background: rgba(255,255,255,0.8);">
            <div class="mb-3">
                <div class="bg-warning bg-opacity-10 text-warning d-inline-flex align-items-center justify-content-center rounded-circle" style="width: 60px; height: 60px;">
                    <i class="fas fa-store fa-2x"></i>
                </div>
            </div>
            <h4 class="fw-bold text-dark">{{ salon.name }}</h4>
            <span class="badge bg-success mb-3 px-3 py-2 rounded-pill">🟢 Activo</span>
            
            <a href="{% url 'marketplace' %}" class="btn btn-outline-dark w-100 rounded-pill mb-2 fw-bold">
                <i class="fas fa-eye me-2"></i> Ver como Cliente
            </a>
            
            <hr class="opacity-10">
            <div class="text-start small text-muted px-2">
                <div class="d-flex justify-content-between mb-1"><span>Servicios:</span> <strong>{{ services.count }}</strong></div>
                <div class="d-flex justify-content-between"><span>Equipo:</span> <strong>{{ employees.count }}</strong></div>
            </div>
        </div>
    </div>

    <div class="col-md-9">
        <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
            <div class="card-header bg-white border-0 pt-4 px-4 pb-0">
                <ul class="nav nav-pills nav-fill gap-2" id="myTab" role="tablist">
                    <li class="nav-item">
                        <button class="nav-link active rounded-pill fw-bold" data-bs-toggle="tab" data-bs-target="#config">
                            ⚙️ Configuración
                        </button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link rounded-pill fw-bold" data-bs-toggle="tab" data-bs-target="#services">
                            ✂️ Servicios
                        </button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link rounded-pill fw-bold" data-bs-toggle="tab" data-bs-target="#team">
                            👥 Equipo
                        </button>
                    </li>
                </ul>
            </div>

            <div class="card-body p-4">
                <div class="tab-content" id="myTabContent">
                    
                    <div class="tab-pane fade show active" id="config">
                        <form method="POST" enctype="multipart/form-data">
                            {% csrf_token %}
                            <input type="hidden" name="update_config" value="1">
                            
                            <h6 class="fw-bold text-muted text-uppercase mb-3 small ls-1">🏢 Información Básica</h6>
                            <div class="form-floating mb-4">
                                {{ config_form.name }}
                                <label>Nombre del Negocio</label>
                            </div>
                            
                            <h6 class="fw-bold text-muted text-uppercase mb-3 small ls-1">📍 Ubicación del Negocio</h6>
                            <div class="row g-3 mb-4">
                                <div class="col-md-8">
                                    <div class="form-floating">
                                        {{ config_form.address }}
                                        <label>Dirección del Local</label>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="form-floating">
                                        {{ config_form.city }}
                                        <label>Ciudad</label>
                                    </div>
                                </div>
                            </div>

                            <h6 class="fw-bold text-muted text-uppercase mb-3 small ls-1">⏰ Horario General</h6>
                            <div class="row g-3 mb-4">
                                <div class="col-md-4">
                                    <div class="form-floating">
                                        {{ config_form.opening_time }}
                                        <label>Apertura</label>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="form-floating">
                                        {{ config_form.closing_time }}
                                        <label>Cierre</label>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="form-floating">
                                        {{ config_form.deposit_percentage }}
                                        <label>% Abono (Reserva)</label>
                                    </div>
                                </div>
                            </div>

                            <h6 class="fw-bold text-muted text-uppercase mb-3 small ls-1 mt-4">
                                <i class="fas fa-share-alt me-2"></i> Redes Sociales
                            </h6>
                            <div class="card bg-white border shadow-sm mb-4 rounded-3 p-3">
                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <div class="form-floating">
                                            {{ config_form.instagram_url }}
                                            <label class="text-muted"><i class="fab fa-instagram text-danger me-2"></i>Link Perfil Instagram</label>
                                        </div>
                                        <div class="form-text small">Ej: https://instagram.com/tu_salon</div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="form-floating">
                                            {{ config_form.whatsapp_number }}
                                            <label class="text-muted"><i class="fab fa-whatsapp text-success me-2"></i>WhatsApp Business</label>
                                        </div>
                                        <div class="form-text small">Ej: 573001234567 (Sin espacios ni +)</div>
                                    </div>
                                </div>
                            </div>

                            <div class="card bg-light border-0 mb-4 rounded-3 overflow-hidden">
                                <div class="card-header bg-info bg-opacity-10 border-0 py-3 d-flex justify-content-between align-items-center">
                                    <h6 class="fw-bold text-info mb-0"><i class="fab fa-telegram me-2"></i> Notificaciones Telegram</h6>
                                    <button type="button" class="btn btn-sm btn-light text-info rounded-pill fw-bold shadow-sm" onclick="testTelegram()">
                                        <i class="fas fa-paper-plane me-1"></i> Probar
                                    </button>
                                </div>
                                <div class="card-body">
                                    <div class="accordion mb-3 shadow-sm rounded-3" id="teleHelp">
                                        <div class="accordion-item border-0">
                                            <h2 class="accordion-header">
                                                <button class="accordion-button collapsed py-2 small fw-bold bg-white" type="button" data-bs-toggle="collapse" data-bs-target="#colTele">
                                                    ❓ ¿Cómo conecto mi Telegram?
                                                </button>
                                            </h2>
                                            <div id="colTele" class="accordion-collapse collapse" data-bs-parent="#teleHelp">
                                                <div class="accordion-body bg-white small text-muted pt-0">
                                                    <ol class="ps-3 mb-0 mt-2 list-group list-group-numbered list-group-flush">
                                                        <li class="list-group-item border-0 p-1">Abrir <a href="https://t.me/BotFather" target="_blank" class="fw-bold text-decoration-none">@BotFather</a> en Telegram.</li>
                                                        <li class="list-group-item border-0 p-1">Enviar el mensaje <code>/newbot</code> y seguir los pasos (ponerle nombre).</li>
                                                        <li class="list-group-item border-0 p-1">Copiar el <strong>Token</strong> rojo que te da y pegarlo aquí abajo.</li>
                                                        <li class="list-group-item border-0 p-1 text-danger fw-bold bg-danger bg-opacity-10 rounded">¡IMPORTANTE! Busca tu nuevo bot y dale al botón "INICIAR" (Start).</li>
                                                        <li class="list-group-item border-0 p-1">Para el Chat ID: Abrir <a href="https://t.me/userinfobot" target="_blank" class="fw-bold text-decoration-none">@userinfobot</a> y copiar el número "Id".</li>
                                                    </ol>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="row g-2">
                                        <div class="col-md-8">
                {{ config_form.telegram_bot_token }}
                <div class="form-text text-muted small mt-1"><i class="fa fa-info-circle"></i> {{ config_form.telegram_bot_token.help_text }}</div>
                </div>
                                        <div class="col-md-4">
                {{ config_form.telegram_chat_id }}
                <div class="form-text text-muted small mt-1"><i class="fa fa-info-circle"></i> {{ config_form.telegram_chat_id.help_text }}</div>
                </div>
                                    </div>
                                    <div id="telegramFeedback" class="mt-2" style="display:none;"></div>
                                </div>
                            </div>

                            <div class="card bg-light border-0 mb-4 rounded-3 overflow-hidden">
                                <div class="card-header bg-danger bg-opacity-10 border-0 py-3">
                                    <h6 class="fw-bold text-danger mb-0"><i class="fas fa-credit-card me-2"></i> Pagos con Bold</h6>
                                </div>
                                <div class="card-body">
                                    <div class="accordion mb-3 shadow-sm rounded-3" id="boldHelp">
                                        <div class="accordion-item border-0">
                                            <h2 class="accordion-header">
                                                <button class="accordion-button collapsed py-2 small fw-bold bg-white text-danger" type="button" data-bs-toggle="collapse" data-bs-target="#colBold">
                                                    ❓ ¿Dónde consigo estas llaves?
                                                </button>
                                            </h2>
                                            <div id="colBold" class="accordion-collapse collapse" data-bs-parent="#boldHelp">
                                                <div class="accordion-body bg-white small text-muted pt-0">
                                                    <ol class="ps-3 mb-0 mt-2 list-group list-group-numbered list-group-flush">
                                                        <li class="list-group-item border-0 p-1">Ingresa a tu <a href="https://panel.bold.co/" target="_blank" class="fw-bold text-decoration-none text-danger">Panel de Bold</a>.</li>
                                                        <li class="list-group-item border-0 p-1">Ve al menú <strong>Desarrolladores</strong> &gt; <strong>Integración</strong>.</li>
                                                        <li class="list-group-item border-0 p-1">Copia el "Identity Key" y el "Secret Key" y pégalos aquí.</li>
                                                        <li class="list-group-item border-0 p-1">En la sección <strong>Webhooks</strong> de Bold, pega el enlace que ves abajo (Webhook URL).</li>
                                                        <li class="list-group-item border-0 p-1 fw-bold">Activa el switch de "Habilitar Webhook" en Bold.</li>
                                                    </ol>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="alert alert-light border shadow-sm d-flex align-items-center p-3 mb-3">
                                        <i class="fas fa-link text-muted fs-4 me-3"></i>
                                        <div class="w-100">
                                            <label class="small fw-bold text-muted text-uppercase">Tu Webhook (Copiar en Bold)</label>
                                            <div class="input-group">
                                                <input type="text" class="form-control bg-white small" value="{{ webhook_url }}" id="webhookInput" readonly>
                                                <button type="button" class="btn btn-dark btn-sm" onclick="copyWebhook()">
                                                    <i class="fas fa-copy"></i>
                                                </button>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="row g-2">
                                        <div class="col-md-6">
                {{ config_form.bold_identity_key }}
                <div class="form-text text-muted small mt-1"><i class="fa fa-info-circle"></i> {{ config_form.bold_identity_key.help_text }}</div>
                </div>
                                        <div class="col-md-6">
                {{ config_form.bold_secret_key }}
                <div class="form-text text-muted small mt-1"><i class="fa fa-info-circle"></i> {{ config_form.bold_secret_key.help_text }}</div>
                </div>
                                    </div>
                                </div>
                            </div>

                            <button type="submit" class="btn btn-primary w-100 rounded-pill py-3 fw-bold shadow-sm">
                                <i class="fas fa-save me-2"></i> Guardar Todo
                            </button>
                        </form>
                    </div>

                    <div class="tab-pane fade" id="services">
                        <div class="text-end mb-3">
                            <button class="btn btn-success rounded-pill shadow-sm px-4 fw-bold" data-bs-toggle="modal" data-bs-target="#addServiceModal">
                                <i class="fas fa-plus me-2"></i> Nuevo Servicio
                            </button>
                        </div>
                        <div class="row g-3">
                            {% for service in services %}
                            <div class="col-md-6">
                                <div class="card h-100 shadow-sm border-0 p-3 flex-row align-items-center justify-content-between">
                                    <div class="d-flex align-items-center gap-3">
                                        <div class="bg-light p-3 rounded-circle text-muted"><i class="fas fa-cut"></i></div>
                                        <div>
                                            <h6 class="fw-bold mb-0 text-dark">{{ service.name }}</h6>
                                            <small class="text-muted">{{ service.duration_minutes }} min • <span class="text-success fw-bold">${{ service.price }}</span></small>
                                        </div>
                                    </div>
                                    <a href="{% url 'delete_service' service.id %}" class="btn btn-light btn-sm text-danger rounded-circle shadow-sm" onclick="return confirm('¿Eliminar?')">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </div>
                            </div>
                            {% empty %}
                            <div class="col-12 text-center py-5 text-muted">
                                <i class="fas fa-box-open fa-3x mb-3 opacity-25"></i>
                                <p>No tienes servicios. ¡Agrega el primero!</p>
                            </div>
                            {% endfor %}
                        </div>
                    </div>

                    <div class="tab-pane fade" id="team">
                        <div class="text-end mb-3">
                            <button class="btn btn-info text-white rounded-pill shadow-sm px-4 fw-bold" data-bs-toggle="modal" data-bs-target="#addEmployeeModal">
                                <i class="fas fa-user-plus me-2"></i> Nuevo Empleado
                            </button>
                        </div>
                        <div class="row g-3">
                            {% for emp in employees %}
                            <div class="col-md-12">
                                <div class="card shadow-sm border-0 p-3">
                                    <div class="d-flex align-items-center justify-content-between">
                                        <div class="d-flex align-items-center gap-3">
                                            <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center fw-bold" style="width: 45px; height: 45px;">
                                                {{ emp.first_name|slice:":1" }}
                                            </div>
                                            <div>
                                                <h6 class="fw-bold mb-0 text-dark">{{ emp.first_name }} {{ emp.last_name }}</h6>
                                                <small class="text-muted">@{{ emp.username }}</small>
                                            </div>
                                        </div>
                                        <span class="badge bg-light text-dark border">Colaborador</span>
                                    </div>
                                </div>
                            </div>
                            {% empty %}
                            <div class="col-12 text-center py-5 text-muted">
                                <p>Aún no tienes equipo. Registra a tus colaboradores.</p>
                            </div>
                            {% endfor %}
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="addServiceModal" tabindex="-1"><div class="modal-dialog"><form method="POST" class="modal-content">{% csrf_token %}<input type="hidden" name="create_service" value="1"><div class="modal-header border-0"><h5 class="fw-bold">Nuevo Servicio</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body"><div class="mb-3"><label class="small fw-bold">Nombre</label>{{ service_form.name }}</div><div class="row"><div class="col-6"><label class="small fw-bold">Duración (min)</label>{{ service_form.duration_minutes }}</div><div class="col-6"><label class="small fw-bold">Precio</label>{{ service_form.price }}</div></div></div><div class="modal-footer border-0"><button class="btn btn-success w-100 rounded-pill">Crear</button></div></form></div></div>

<div class="modal fade" id="addEmployeeModal" tabindex="-1"><div class="modal-dialog"><form method="POST" class="modal-content">{% csrf_token %}<input type="hidden" name="create_employee" value="1"><div class="modal-header border-0"><h5 class="fw-bold">Registrar Empleado</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div><div class="modal-body"><div class="row mb-3"><div class="col-6">{{ employee_form.first_name }}</div><div class="col-6">{{ employee_form.last_name }}</div></div><div class="mb-3"><label class="small fw-bold">Usuario</label>{{ employee_form.username }}</div><div class="mb-3"><label class="small fw-bold">Email</label>{{ employee_form.email }}</div><div class="mb-3"><label class="small fw-bold">Contraseña</label>{{ employee_form.password }}</div></div><div class="modal-footer border-0"><button class="btn btn-info text-white w-100 rounded-pill">Registrar</button></div></form></div></div>

<script>
function copyWebhook() {
    var copyText = document.getElementById("webhookInput");
    copyText.select();
    navigator.clipboard.writeText(copyText.value);
    alert("Enlace copiado: " + copyText.value);
}

function testTelegram() {
    const token = document.querySelector('input[name*="telegram_bot_token"]').value;
    const chat = document.querySelector('input[name*="telegram_chat_id"]').value;
    const fb = document.getElementById('telegramFeedback');
    
    if(!token || !chat) { alert('Llena los campos primero.'); return; }
    
    fb.style.display = 'block';
    fb.innerHTML = '<span class="text-muted"><i class="fas fa-spinner fa-spin"></i> Conectando...</span>';
    
    fetch('/api/test-telegram/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
        body: JSON.stringify({token: token, chat_id: chat})
    }).then(r=>r.json()).then(d=>{
        fb.innerHTML = d.success ? 
            '<span class="text-success fw-bold"><i class="fas fa-check"></i> ¡Éxito! Revisa tu chat.</span>' : 
            '<span class="text-danger fw-bold"><i class="fas fa-times"></i> ' + d.message + '</span>';
    });
}
</script>
{% endblock %}
"""

def write_file(path, content):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Archivo reparado: {path}")
    except Exception as e:
        print(f"❌ Error escribiendo {path}: {e}")

if __name__ == "__main__":
    print("🔮 Iniciando reparación mágica del ecosistema...")
    write_file('apps/users/models.py', users_models_content)
    write_file('apps/businesses/views.py', businesses_views_content)
    write_file('templates/owner_dashboard.html', owner_dashboard_content)
    print("\\n✨ ¡Archivos corregidos! Ahora ejecuta: 'python manage.py makemigrations' y 'python manage.py migrate'")