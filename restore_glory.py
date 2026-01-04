import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

FORMS_PATH = os.path.join(APP_DIR, "forms.py")
VIEWS_PATH = os.path.join(APP_DIR, "views.py")
MASTER_HTML_PATH = os.path.join(TEMPLATES_DIR, "master.html")
REGISTER_HTML_PATH = os.path.join(TEMPLATES_DIR, "registration", "register_owner.html")

# --- 1. LISTA DE CIUDADES Y FORMS.PY MEJORADO ---
# (He incluido las principales, puedes agregar más si quieres)
COLOMBIA_CITIES = [
    ('', 'Selecciona tu Ciudad...'),
    ('Bogotá', 'Bogotá D.C.'),
    ('Medellín', 'Medellín'),
    ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'),
    ('Cartagena', 'Cartagena'),
    ('Bucaramanga', 'Bucaramanga'),
    ('Manizales', 'Manizales'),
    ('Pereira', 'Pereira'),
    ('Cúcuta', 'Cúcuta'),
    ('Ibagué', 'Ibagué'),
    ('Santa Marta', 'Santa Marta'),
    ('Villavicencio', 'Villavicencio'),
    ('Pasto', 'Pasto'),
    ('Montería', 'Montería'),
    ('Valledupar', 'Valledupar'),
    ('Armenia', 'Armenia'),
    ('Neiva', 'Neiva'),
    ('Popayán', 'Popayán'),
    ('Tunja', 'Tunja'),
    ('Riohacha', 'Riohacha'),
    ('Sincelejo', 'Sincelejo'),
    ('Florencia', 'Florencia'),
    ('Yopal', 'Yopal'),
    ('Quibdó', 'Quibdó'),
]

CONTENIDO_FORMS = f"""from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee, SalonSchedule

User = get_user_model()

# --- 1. REGISTRO DUEÑO ---
class OwnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={{'class': 'form-control', 'placeholder': 'Crea tu contraseña'}}), label="Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={{'class': 'form-control', 'placeholder': 'Repite la contraseña'}}), label="Confirmar")
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {{
            'first_name': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Tu Nombre'}}),
            'last_name': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Tu Apellido'}}),
            'email': forms.EmailInput(attrs={{'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}}),
            'username': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Usuario para login'}}),
        }}
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("password_confirm"):
            raise forms.ValidationError("Las contraseñas no coinciden.")

class SalonForm(forms.ModelForm):
    # Campo personalizado de ciudad con lista desplegable
    city = forms.ChoiceField(choices={COLOMBIA_CITIES}, widget=forms.Select(attrs={{'class': 'form-select'}}), label="Ciudad")

    class Meta:
        model = Salon
        # Quitamos 'whatsapp' de aquí porque lo llenaremos automáticamente con el teléfono
        fields = ['name', 'address', 'city', 'phone', 'instagram']
        labels = {{
            'name': 'Nombre del Negocio',
            'address': 'Dirección (Maps)',
            'phone': 'Celular / WhatsApp',
            'instagram': 'Usuario Instagram',
        }}
        widgets = {{
            'name': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Ej: Barbería El Rey'}}),
            'address': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Ej: Calle 123 # 45-67'}}),
            'phone': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Ej: 300 123 4567'}}),
            'instagram': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Ej: barberia_elrey (sin @)'}}),
        }}

# --- OTROS FORMULARIOS ---
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'price']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'phone', 'email']

class EmployeeCreationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={{'class': 'form-control'}}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={{'class': 'form-control'}}))
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'phone', 'email']

class SalonScheduleForm(forms.ModelForm):
    class Meta:
        model = SalonSchedule
        fields = ['monday_open', 'tuesday_open', 'wednesday_open', 'thursday_open', 'friday_open', 'saturday_open', 'sunday_open']
"""

# --- 2. VIEWS.PY (LOGICA DE TELEFONO DUPLICADO) ---
CONTENIDO_VIEWS = """from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView, ListView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, date, time
from .models import Salon, Service, Employee, SalonSchedule, EmployeeSchedule, Booking
from .forms import (
    OwnerRegistrationForm, SalonForm, ServiceForm, 
    EmployeeForm, EmployeeCreationForm, SalonScheduleForm
)

User = get_user_model()

# --- VISTA DE REGISTRO MEJORADA ---
class RegisterOwnerView(CreateView):
    template_name = 'registration/register_owner.html'
    form_class = OwnerRegistrationForm
    success_url = '/dashboard/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user_form'] = OwnerRegistrationForm()
        ctx['salon_form'] = SalonForm()
        return ctx

    def post(self, request, *args, **kwargs):
        user_form = OwnerRegistrationForm(request.POST)
        salon_form = SalonForm(request.POST)
        
        if user_form.is_valid() and salon_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            salon = salon_form.save(commit=False)
            salon.owner = user
            
            # TRUCO: Copiamos el teléfono al campo whatsapp automáticamente
            salon.whatsapp = salon_form.cleaned_data['phone']
            
            salon.save()
            SalonSchedule.objects.create(salon=salon)
            login(request, user)
            return redirect('owner_dashboard')
        
        return render(request, self.template_name, {'user_form': user_form, 'salon_form': salon_form})

# --- OTRAS VISTAS (MANTENIDAS) ---
def home(request): return render(request, 'home.html')
def marketplace(request): return render(request, 'marketplace.html', {'salons': Salon.objects.all()})
def salon_detail(request, salon_id): return render(request, 'salon_detail.html', {'salon': get_object_or_404(Salon, id=salon_id)})
def landing_businesses(request): return render(request, 'landing_businesses.html')

@login_required
def booking_wizard(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)
    return render(request, 'booking/step_calendar.html', {'salon': salon})

@login_required
def client_dashboard(request):
    bookings = Booking.objects.filter(customer=request.user).order_by('-date')
    return render(request, 'client_dashboard.html', {'bookings': bookings})

@login_required
def dashboard_redirect(request):
    if hasattr(request.user, 'salon'): return redirect('owner_dashboard')
    elif hasattr(request.user, 'employee_profile'): return redirect('employee_dashboard')
    else: return redirect('client_dashboard')

@method_decorator(login_required, name='dispatch')
class OwnerDashboardView(TemplateView):
    template_name = 'dashboard/owner_dashboard.html'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try: ctx['salon'] = self.request.user.salon
        except: ctx['salon'] = None
        if ctx['salon']:
            ctx['pending_bookings'] = Booking.objects.filter(salon=ctx['salon'], status='pending')
        return ctx

@method_decorator(login_required, name='dispatch')
class OwnerServicesView(ListView):
    model = Service
    template_name = 'dashboard/owner_services.html'
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class ServiceCreateView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'dashboard/service_form.html'
    success_url = reverse_lazy('owner_services')
    def form_valid(self, form):
        form.instance.salon = self.request.user.salon
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class ServiceUpdateView(UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'dashboard/service_form.html'
    success_url = reverse_lazy('owner_services')
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class ServiceDeleteView(DeleteView):
    model = Service
    success_url = reverse_lazy('owner_services')
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class OwnerEmployeesView(ListView):
    model = Employee
    template_name = 'dashboard/owner_employees.html'
    def get_queryset(self): return Employee.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeCreationForm
    template_name = 'dashboard/employee_form.html'
    success_url = reverse_lazy('owner_employees')
    def form_valid(self, form):
        user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password'])
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        employee = form.save(commit=False)
        employee.salon = self.request.user.salon
        employee.user = user
        employee.save()
        EmployeeSchedule.objects.create(employee=employee)
        return super().form_valid(form)
        
@method_decorator(login_required, name='dispatch')
class OwnerSettingsView(UpdateView):
    model = SalonSchedule
    template_name = 'dashboard/owner_settings.html'
    form_class = SalonScheduleForm
    success_url = reverse_lazy('owner_settings')
    def get_object(self, queryset=None):
        schedule, created = SalonSchedule.objects.get_or_create(salon=self.request.user.salon)
        return schedule

@login_required
def employee_dashboard(request):
    return render(request, 'employee_dashboard.html', {'employee': request.user.employee_profile})
"""

# --- 3. MASTER.HTML (RECUPERANDO EL MENÚ PERDIDO) ---
CONTENIDO_MASTER = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paso Ecosystem | El Sistema de tu Negocio</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f8f9fa; display: flex; flex-direction: column; min-height: 100vh; }
        .navbar { box-shadow: 0 4px 15px rgba(0,0,0,0.05); background-color: #ffffff; padding: 15px 0; }
        .navbar-brand { font-weight: 800; letter-spacing: -0.5px; font-size: 1.4rem; color: #111; }
        .nav-link { font-weight: 500; color: #555 !important; margin-left: 10px; transition: 0.2s; }
        .nav-link:hover { color: #000 !important; }
        .btn-primary { background-color: #111; border: none; padding: 10px 24px; font-weight: 600; transition: 0.3s; }
        .btn-primary:hover { background-color: #333; transform: translateY(-1px); }
        .btn-outline-dark { padding: 8px 20px; font-weight: 600; }
        main { flex: 1; }
        footer { background: #111; color: #fff; padding: 40px 0; margin-top: auto; }
    </style>
</head>
<body>

    <nav class="navbar navbar-expand-lg fixed-top">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="bi bi-grid-3x3-gap-fill text-warning me-2"></i>PASO<span class="text-secondary">ECO</span>
            </a>
            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-center">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'home' %}">Inicio</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'marketplace' %}">Buscar Servicios</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'landing_businesses' %}">Soy Negocio</a>
                    </li>
                    
                    {% if user.is_authenticated %}
                        <li class="nav-item ms-3">
                            <a class="btn btn-warning rounded-pill px-4" href="{% url 'dashboard_redirect' %}">
                                <i class="bi bi-speedometer2 me-1"></i> Mi Panel
                            </a>
                        </li>
                        <li class="nav-item ms-2">
                             <form action="{% url 'logout' %}" method="post" class="d-inline">
                                {% csrf_token %}
                                <button type="submit" class="btn btn-link nav-link text-danger" style="text-decoration:none;">
                                    <i class="bi bi-box-arrow-right"></i>
                                </button>
                            </form>
                        </li>
                    {% else %}
                        <li class="nav-item ms-3">
                            <a class="nav-link" href="{% url 'login' %}">Ingresar</a>
                        </li>
                        <li class="nav-item ms-2">
                            <a class="btn btn-primary rounded-pill text-white shadow-sm" href="{% url 'register_owner' %}">
                                Registrar Negocio
                            </a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div style="height: 80px;"></div>

    <main>
        {% block content %}
        {% endblock %}
    </main>

    <footer>
        <div class="container text-center">
            <h5 class="fw-bold mb-3">PASO ECOSYSTEM</h5>
            <p class="text-white-50 small">El estándar de la belleza digital en Colombia.</p>
            <div class="mt-4">
                <i class="bi bi-instagram mx-2"></i>
                <i class="bi bi-whatsapp mx-2"></i>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# --- 4. HTML DE REGISTRO (SIN EL CAMPO WHATSAPP DUPLICADO) ---
CONTENIDO_REGISTRO = """{% extends 'master.html' %}
{% load static %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-7">
            <div class="card shadow-lg border-0 rounded-4 overflow-hidden">
                <div class="card-header bg-dark text-white text-center py-4">
                    <h3 class="fw-bold mb-0">Comienza tu prueba gratis</h3>
                    <p class="mb-0 small text-white-50">Configura tu negocio en menos de 2 minutos</p>
                </div>
                <div class="card-body p-5 bg-white">
                    <form method="post">
                        {% csrf_token %}
                        
                        {% if user_form.errors or salon_form.errors %}
                            <div class="alert alert-danger rounded-3 small">
                                <i class="bi bi-exclamation-triangle-fill me-2"></i> Por favor revisa los campos en rojo.
                            </div>
                        {% endif %}

                        <h6 class="text-uppercase fw-bold text-muted mb-3"><i class="bi bi-person-badge me-2"></i> Tus Datos</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-6">
                                <label class="form-label small fw-bold">Nombre</label>
                                {{ user_form.first_name }}
                            </div>
                            <div class="col-6">
                                <label class="form-label small fw-bold">Apellido</label>
                                {{ user_form.last_name }}
                            </div>
                            <div class="col-12">
                                <label class="form-label small fw-bold">Correo (Usuario)</label>
                                {{ user_form.email }}
                            </div>
                            <div class="col-12">
                                <label class="form-label small fw-bold">Crea tu Usuario de Acceso</label>
                                {{ user_form.username }}
                            </div>
                            <div class="col-6">
                                <label class="form-label small fw-bold">Contraseña</label>
                                {{ user_form.password }}
                            </div>
                            <div class="col-6">
                                <label class="form-label small fw-bold">Confirmar</label>
                                {{ user_form.password_confirm }}
                            </div>
                        </div>

                        <h6 class="text-uppercase fw-bold text-muted mb-3 border-top pt-4"><i class="bi bi-shop me-2"></i> Datos del Negocio</h6>
                        <div class="row g-3 mb-4">
                            <div class="col-12">
                                <label class="form-label small fw-bold">Nombre del Local</label>
                                {{ salon_form.name }}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold">Ciudad</label>
                                {{ salon_form.city }} </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold">Celular / WhatsApp</label>
                                {{ salon_form.phone }}
                            </div>
                            <div class="col-12">
                                <label class="form-label small fw-bold">Dirección</label>
                                {{ salon_form.address }}
                            </div>
                            <div class="col-12">
                                <label class="form-label small fw-bold text-danger"><i class="bi bi-instagram"></i> Instagram</label>
                                {{ salon_form.instagram }}
                            </div>
                        </div>

                        <div class="d-grid mt-5">
                            <button type="submit" class="btn btn-warning btn-lg fw-bold shadow-sm">
                                🚀 Lanchar mi Negocio
                            </button>
                        </div>
                    </form>
                </div>
                <div class="card-footer text-center bg-light py-3">
                    <small>¿Ya tienes cuenta? <a href="{% url 'login' %}" class="fw-bold text-dark">Inicia Sesión</a></small>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

def restaurar_gloria():
    print("✨ Restaurando el alma del proyecto...")
    
    # 1. Forms con Ciudades
    print("   🌆 Inyectando lista de ciudades y simplificando forms.py...")
    with open(FORMS_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_FORMS)

    # 2. Views con lógica de Teléfono doble
    print("   🧠 Actualizando views.py para manejar el teléfono único...")
    with open(VIEWS_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_VIEWS)

    # 3. Master HTML con Menú Original
    print("   🧭 Recuperando el Navbar original en master.html...")
    with open(MASTER_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_MASTER)

    # 4. Registro Limpio
    print("   📝 Actualizando formulario de registro (register_owner.html)...")
    with open(REGISTER_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_REGISTRO)

    print("✅ ¡Restauración completa! Ciudades, Menú y Formulario optimizados.")

if __name__ == "__main__":
    restaurar_gloria()