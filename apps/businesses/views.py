import json
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
