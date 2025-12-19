import os

# 1. CÓDIGO CORRECTO PARA VIEWS.PY (Arregla Error 500 y Rutas)
views_content = """from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import datetime
import uuid

# --- IMPORTACIONES CORREGIDAS ---
from apps.users.forms import CustomUserCreationForm
from apps.businesses.models import (
    Salon, Service, Booking, Employee, OpeningHours, EmployeeSchedule
)
from apps.businesses.forms import (
    SalonForm, ServiceForm, OpeningHoursForm, BookingForm, 
    EmployeeSettingsForm, EmployeeScheduleForm
)

def home(request):
    salons = Salon.objects.all()
    # Usamos set() para evitar duplicados y sorted para ordenar
    ciudades = sorted(list(set(Salon.objects.values_list('city', flat=True))))
    return render(request, 'home.html', {'salons': salons, 'ciudades': ciudades})

def register(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'role', 'CUSTOMER') == 'ADMIN': return redirect('dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.first_name}!')
            if getattr(user, 'role', 'CUSTOMER') == 'ADMIN': return redirect('dashboard')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def salon_detail(request, slug):
    salon = get_object_or_404(Salon, slug=slug)
    services = salon.services.all()
    is_open = getattr(salon, 'is_open', False)
    return render(request, 'salon_detail.html', {'salon': salon, 'services': services, 'is_open': is_open})

@login_required
def dashboard(request):
    # 1. Seguridad
    if getattr(request.user, 'role', 'CUSTOMER') != 'ADMIN':
        if getattr(request.user, 'role', 'CUSTOMER') == 'EMPLOYEE': return redirect('employee_dashboard')
        return redirect('home')

    # 2. Obtener o Crear Salón
    try:
        salon = request.user.salon
    except Exception:
        if request.method == 'POST':
            form = SalonForm(request.POST, request.FILES)
            if form.is_valid():
                salon = form.save(commit=False)
                salon.owner = request.user
                salon.save()
                for i in range(6): OpeningHours.objects.create(salon=salon, weekday=i, from_hour=datetime.time(8,0), to_hour=datetime.time(20,0))
                OpeningHours.objects.create(salon=salon, weekday=6, from_hour=datetime.time(9,0), to_hour=datetime.time(15,0), is_closed=True)
                messages.success(request, '¡Negocio creado!')
                return redirect('dashboard')
        else:
            form = SalonForm()
        return render(request, 'dashboard/create_salon.html', {'form': form})

    # 3. Inicializar Forms (Evita error 500)
    form = SalonForm(instance=salon)
    s_form = ServiceForm()
    h_form = OpeningHoursForm()

    if request.method == 'POST':
        if 'update_settings' in request.POST:
            form = SalonForm(request.POST, request.FILES, instance=salon)
            if form.is_valid():
                form.save()
                messages.success(request, 'Guardado.')
                return redirect('dashboard')
        elif 'create_service' in request.POST:
            s_form = ServiceForm(request.POST)
            if s_form.is_valid():
                srv = s_form.save(commit=False)
                srv.salon = salon
                srv.save()
                messages.success(request, 'Servicio creado.')
                return redirect('dashboard')
        elif 'update_hours' in request.POST:
            h_form = OpeningHoursForm(request.POST)
            if h_form.is_valid():
                day = h_form.cleaned_data['weekday']
                OpeningHours.objects.update_or_create(salon=salon, weekday=day, defaults={'from_hour': h_form.cleaned_data['from_hour'], 'to_hour': h_form.cleaned_data['to_hour'], 'is_closed': h_form.cleaned_data['is_closed']})
                messages.success(request, 'Horario actualizado.')
                return redirect('dashboard')

    # 4. Contexto Seguro
    try:
        if not salon.invite_token:
            salon.invite_token = uuid.uuid4()
            salon.save(update_fields=['invite_token'])
        invite_link = f"http://{request.get_host()}/unete/{salon.invite_token}/"
    except:
        invite_link = "#"

    return render(request, 'dashboard/index.html', {
        'salon': salon, 'form': form, 's_form': s_form, 'h_form': h_form,
        'services': salon.services.all(), 'bookings': salon.bookings.all().order_by('-start_time'),
        'employees': salon.employees.all(), 'hours': salon.opening_hours.all().order_by('weekday'),
        'invite_link': invite_link, 'webhook_url': f"http://{request.get_host()}/api/webhooks/bold/"
    })

@login_required
def employee_join(request, token):
    salon = get_object_or_404(Salon, invite_token=token)
    if Employee.objects.filter(user=request.user, salon=salon).exists(): return redirect('employee_dashboard')
    if request.method == 'POST':
        employee = Employee.objects.create(user=request.user, salon=salon)
        request.user.role = 'EMPLOYEE'
        request.user.save()
        for i in range(5): EmployeeSchedule.objects.create(employee=employee, weekday=i, from_hour=datetime.time(9,0), to_hour=datetime.time(18,0))
        messages.success(request, '¡Bienvenido!')
        return redirect('employee_dashboard')
    return render(request, 'registration/employee_join.html', {'salon': salon})

@login_required
def employee_dashboard(request):
    try: employee = request.user.employee
    except: return redirect('home')
    settings_form = EmployeeSettingsForm(instance=employee)
    schedule_form = EmployeeScheduleForm()
    if request.method == 'POST':
        if 'update_keys' in request.POST:
            settings_form = EmployeeSettingsForm(request.POST, instance=employee)
            if settings_form.is_valid(): settings_form.save(); messages.success(request, 'Guardado.'); return redirect('employee_dashboard')
        elif 'update_schedule' in request.POST:
            schedule_form = EmployeeScheduleForm(request.POST)
            if schedule_form.is_valid():
                EmployeeSchedule.objects.update_or_create(employee=employee, weekday=schedule_form.cleaned_data['weekday'], defaults={'from_hour': schedule_form.cleaned_data['from_hour'], 'to_hour': schedule_form.cleaned_data['to_hour'], 'is_closed': schedule_form.cleaned_data['is_closed']})
                messages.success(request, 'Actualizado.')
                return redirect('employee_dashboard')
    return render(request, 'dashboard/employee_dashboard.html', {'employee': employee, 'appointments': Booking.objects.filter(employee=employee).order_by('start_time'), 'my_schedule': employee.schedule.all().order_by('weekday'), 'settings_form': settings_form, 'schedule_form': schedule_form})

def booking_create(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = BookingForm(request.POST, service=service)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.service = service
            booking.salon = service.salon
            booking.end_time = booking.start_time + datetime.timedelta(minutes=service.duration_minutes)
            if form.cleaned_data.get('employee'): booking.employee = form.cleaned_data['employee']
            else: booking.employee = service.salon.employees.first()
            booking.save()
            return redirect('booking_success')
    else: form = BookingForm(service=service)
    return render(request, 'booking_form.html', {'form': form, 'service': service})

def booking_success(request): return render(request, 'booking_success.html')
def api_get_availability(request): return JsonResponse({'status': 'ok'})
@csrf_exempt
def bold_webhook(request): return HttpResponse("OK")
"""

# 2. CÓDIGO CORRECTO PARA FORMS.PY (Asegura el nombre SalonForm)
forms_content = """from django import forms
from django.utils import timezone
from .models import Salon, Service, OpeningHours, Booking, Employee, EmployeeSchedule

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corte de Cabello'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Breve descripción...'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class EmployeeCreationForm(forms.Form):
    name = forms.CharField(label="Nombre", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(label="Teléfono", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'slug', 'description', 'city', 'address', 'phone', 'latitude', 'longitude', 'logo', 'banner', 'instagram', 'facebook', 'tiktok', 'bold_api_key', 'bold_signing_key', 'telegram_bot_token', 'telegram_chat_id']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'tiktok': forms.URLInput(attrs={'class': 'form-control'}),
            'bold_api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'bold_signing_key': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram_bot_token': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram_chat_id': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = ['name', 'city', 'address', 'phone']
        for field in self.fields: 
            if field not in required_fields: self.fields[field].required = False

class OpeningHoursForm(forms.ModelForm):
    class Meta:
        model = OpeningHours
        fields = ['weekday', 'from_hour', 'to_hour', 'is_closed']
        widgets = {'weekday': forms.Select(attrs={'class': 'form-select'}), 'from_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), 'to_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), 'is_closed': forms.CheckboxInput(attrs={'class': 'form-check-input'})}

class BookingForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Employee.objects.none(), required=False, empty_label="Cualquiera", widget=forms.Select(attrs={'class': 'form-select'}))
    class Meta:
        model = Booking
        fields = ['employee', 'customer_name', 'customer_phone', 'start_time']
        widgets = {'customer_name': forms.TextInput(attrs={'class': 'form-control'}), 'customer_phone': forms.TextInput(attrs={'class': 'form-control'}), 'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})}
    def __init__(self, *args, **kwargs):
        service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)
        if service: self.fields['employee'].queryset = service.salon.employees.all()
    def clean_start_time(self):
        start_time = self.cleaned_data['start_time']
        if start_time < timezone.now(): raise forms.ValidationError("Fecha inválida")
        return start_time

class EmployeeSettingsForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['lunch_start', 'lunch_end', 'bold_api_key', 'bold_signing_key', 'telegram_bot_token', 'telegram_chat_id']
        widgets = {'lunch_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), 'lunch_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), 'bold_api_key': forms.TextInput(attrs={'class': 'form-control'}), 'bold_signing_key': forms.TextInput(attrs={'class': 'form-control'}), 'telegram_bot_token': forms.TextInput(attrs={'class': 'form-control'}), 'telegram_chat_id': forms.TextInput(attrs={'class': 'form-control'})}

class EmployeeScheduleForm(forms.ModelForm):
    class Meta:
        model = EmployeeSchedule
        fields = ['weekday', 'from_hour', 'to_hour', 'is_closed']
        widgets = {'weekday': forms.Select(attrs={'class': 'form-select', 'disabled': 'disabled'}), 'from_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), 'to_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), 'is_closed': forms.CheckboxInput(attrs={'class': 'form-check-input'})}
"""

# 3. CÓDIGO CORRECTO PARA BASE.HTML (Iconos visibles)
base_html_content = """{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}PASO Beauty Ecosystem{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
</head>
<body class="d-flex flex-column min-vh-100">
    <nav class="navbar navbar-expand-lg sticky-top">
        <div class="container">
            <a class="navbar-brand" href="{% url 'home' %}"><i class="bi bi-stars"></i> PASO</a>
            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"><span class="navbar-toggler-icon"></span></button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-center gap-3">
                    <li class="nav-item"><a class="nav-link" href="{% url 'home' %}">Inicio</a></li>
                    {% if user.is_authenticated %}
                        {% if user.role == 'ADMIN' %}
                            <li class="nav-item"><a class="btn btn-primary btn-sm rounded-pill px-3" href="{% url 'dashboard' %}">Mi Negocio</a></li>
                        {% elif user.role == 'EMPLOYEE' %}
                            <li class="nav-item"><a class="btn btn-primary btn-sm rounded-pill px-3" href="{% url 'employee_dashboard' %}">Mi Agenda</a></li>
                        {% endif %}
                        <li class="nav-item"><form action="{% url 'logout' %}" method="post" class="d-inline">{% csrf_token %}<button type="submit" class="btn btn-outline-danger btn-sm rounded-pill border-0">Salir</button></form></li>
                    {% else %}
                        <li class="nav-item"><a class="nav-link" href="{% url 'login' %}">Entrar</a></li>
                        <li class="nav-item"><a class="btn btn-nav-action" href="{% url 'register' %}">Crear Cuenta</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    <div class="container mt-3 position-absolute start-0 end-0" style="z-index: 2000; pointer-events: none;">
        {% if messages %}
            <div class="row justify-content-center"><div class="col-md-6">{% for message in messages %}<div class="alert alert-{{ message.tags }} alert-dismissible fade show shadow-sm" style="pointer-events: auto;">{{ message }}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>{% endfor %}</div></div>
        {% endif %}
    </div>
    <main class="flex-grow-1">{% block content %}{% endblock %}</main>
    <footer class="text-center py-4 mt-auto border-top bg-white"><small class="text-muted">&copy; 2025 PASO Beauty.</small></footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# 4. CÓDIGO CORRECTO PARA MAIN.CSS (Botón GPS visible)
css_content = """@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root { --bg-base: #f8fafc; --text-main: #0f172a; --text-muted: #64748b; --primary-gradient: linear-gradient(135deg, #0f172a 0%, #334155 100%); --accent-gradient: linear-gradient(to right, #ec4899, #8b5cf6); --glass-bg: rgba(255, 255, 255, 0.7); --glass-border: rgba(255, 255, 255, 0.5); --card-radius: 28px; --shadow-soft: 0 10px 40px -10px rgba(0,0,0,0.08); }
body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: var(--bg-base); color: var(--text-main); overflow-x: hidden; position: relative; display: flex; flex-direction: column; min-height: 100vh; }
.ambient-bg { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; overflow: hidden; background: radial-gradient(circle at 50% 50%, #fff, #f1f5f9); }
.blob { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.6; animation: float 10s infinite ease-in-out; }
.blob-1 { width: 600px; height: 600px; background: #fce7f3; top: -10%; left: -10%; animation-delay: 0s; }
.blob-2 { width: 500px; height: 500px; background: #ede9fe; bottom: -10%; right: -5%; animation-delay: 2s; }
.blob-3 { width: 300px; height: 300px; background: #dbeafe; top: 40%; left: 30%; animation-delay: 4s; }
@keyframes float { 0%, 100% { transform: translate(0, 0) scale(1); } 33% { transform: translate(30px, -50px) scale(1.1); } 66% { transform: translate(-20px, 20px) scale(0.9); } }
.navbar { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255, 255, 255, 0.1); transition: all 0.3s ease; padding: 1rem 0; }
.navbar.scrolled { background: rgba(255, 255, 255, 0.85); box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05); border-bottom: 1px solid rgba(0, 0, 0, 0.05); }
.navbar-brand { font-weight: 800; font-size: 1.5rem; color: var(--text-main) !important; letter-spacing: -0.5px; }
.navbar-brand i { color: #ec4899; }
.nav-link { font-weight: 600; color: var(--text-main) !important; font-size: 0.95rem; }
.btn-nav-action { background-color: var(--text-main); color: #fff !important; border-radius: 50px; padding: 8px 24px; font-weight: 600; box-shadow: 0 4px 14px rgba(15, 23, 42, 0.2); transition: all 0.3s ease; }
.btn-nav-action:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(15, 23, 42, 0.3); }
.hero-section { padding: 100px 0 60px; text-align: center; position: relative; z-index: 1; }
.hero-title { font-size: 4.5rem; font-weight: 800; line-height: 1.1; letter-spacing: -2px; margin-bottom: 1.5rem; background: linear-gradient(to right, #0f172a 40%, #475569); -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: fadeUp 0.8s ease-out; }
.hero-title span { background: var(--accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-subtitle { font-size: 1.25rem; color: var(--text-muted); font-weight: 500; max-width: 600px; margin: 0 auto 3rem; animation: fadeUp 1s ease-out; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.search-container { background: rgba(255, 255, 255, 0.6); backdrop-filter: blur(20px); border: 1px solid #fff; border-radius: 50px; padding: 8px 15px; box-shadow: 0 20px 40px -10px rgba(0,0,0,0.1); display: flex; align-items: center; gap: 10px; max-width: 750px; margin: 0 auto 4rem; animation: fadeUp 1.2s ease-out; }
.search-input { border: none; background: transparent; padding: 12px 15px; font-size: 1rem; color: var(--text-main); width: 100%; outline: none; }
.search-input:focus { outline: none; }
.btn-location-pulse { background: #ffffff !important; color: #ec4899 !important; border: 2px solid #ec4899; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; cursor: pointer; box-shadow: 0 4px 15px rgba(236, 72, 153, 0.2); transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); position: relative; overflow: visible; flex-shrink: 0; z-index: 99; }
.btn-location-pulse:hover { background: var(--accent-gradient) !important; color: #fff !important; border-color: transparent; transform: translateY(-2px) scale(1.1); box-shadow: 0 8px 25px rgba(236, 72, 153, 0.4); }
.salon-card { background: #fff; border-radius: var(--card-radius); border: 1px solid rgba(255,255,255,0.8); box-shadow: var(--shadow-soft); transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); overflow: hidden; height: 100%; position: relative; text-decoration: none !important; display: block; }
.salon-card:hover { transform: translateY(-10px) scale(1.02); box-shadow: 0 20px 50px -10px rgba(0,0,0,0.15); z-index: 2; }
.card-img-top { height: 200px; object-fit: cover; width: 100%; border-bottom: 1px solid #f1f5f9; }
.card-body { padding: 1.5rem; }
.salon-avatar { width: 48px; height: 48px; background: linear-gradient(135deg, #e2e8f0, #cbd5e1); border-radius: 14px; display: flex; align-items: center; justify-content: center; font-weight: 700; color: var(--text-main); font-size: 1.2rem; margin-right: 15px; }
.status-pill { font-size: 0.7rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; display: inline-flex; align-items: center; gap: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
.status-open { background-color: #dcfce7; color: #166534; }
.status-open::before { content: ''; display: block; width: 6px; height: 6px; background-color: #166534; border-radius: 50%; }
.status-closed { background-color: #fee2e2; color: #991b1b; }
.status-closed::before { content: ''; display: block; width: 6px; height: 6px; background-color: #991b1b; border-radius: 50%; }
.card-title { font-weight: 700; color: var(--text-main); font-size: 1.1rem; margin-bottom: 0.2rem; }
.card-location { color: var(--text-muted); font-size: 0.9rem; display: flex; align-items: center; gap: 5px; }
footer { background-color: #fff; border-top: 1px solid #f1f5f9; color: var(--text-muted); }
@media (max-width: 768px) { .hero-title { font-size: 2.8rem; } .search-container { flex-direction: column; padding: 15px; border-radius: 28px; } .btn-location-pulse { width: 100%; border-radius: 14px; margin-top: 10px; } }
"""

# DICCIONARIO DE ARCHIVOS A SOBRESCRIBIR
files_to_fix = {
    "config/views.py": views_content,
    "apps/businesses/forms.py": forms_content,
    "templates/base.html": base_html_content,
    "static/css/main.css": css_content
}

# PROCESO DE ESCRITURA
print("✨ INICIANDO SCRIPT MÁGICO DE REPARACIÓN ✨")
for path, content in files_to_fix.items():
    try:
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Escribir el archivo
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Arreglado: {path}")
    except Exception as e:
        print(f"❌ Error en {path}: {e}")

print("\n🚀 LISTO! Ahora ejecuta estos comandos en tu terminal:")
print("git add .")
print('git commit -m "Reparacion magica automatica"')
print("git push origin main")