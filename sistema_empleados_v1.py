import os
import sys

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
MODELS_PATH = os.path.join(APP_DIR, "models.py")
FORMS_PATH = os.path.join(APP_DIR, "forms.py")
VIEWS_PATH = os.path.join(APP_DIR, "views.py")
URLS_PATH = os.path.join(APP_DIR, "urls.py")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates", "dashboard")
EMPLOYEE_FORM_HTML = os.path.join(TEMPLATES_DIR, "employee_form.html")
EMPLOYEE_DASHBOARD_HTML = os.path.join(BASE_DIR, "templates", "employee_dashboard.html")

# --- 1. ACTUALIZAR MODELOS (Agregamos User a Empleado y HorarioEmpleado) ---
CONTENIDO_MODELS = """from django.db import models
from django.conf import settings

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salon')
    name = models.CharField(max_length=255, verbose_name="Nombre del Negocio")
    description = models.TextField(verbose_name="Descripción", blank=True)
    address = models.CharField(max_length=255, verbose_name="Dirección Física")
    phone = models.CharField(max_length=50, verbose_name="Teléfono", blank=True, default='')
    email = models.EmailField(verbose_name="Correo del Negocio", blank=True)
    whatsapp = models.CharField(max_length=50, blank=True, verbose_name="WhatsApp")
    instagram = models.CharField(max_length=100, blank=True, verbose_name="Instagram")

    def __str__(self):
        return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100, verbose_name="Nombre del Servicio")
    description = models.TextField(blank=True, verbose_name="Descripción")
    duration_minutes = models.IntegerField(default=30, verbose_name="Duración (min)")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Precio")

    def __str__(self):
        return self.name

class Employee(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='employees')
    # --- CONEXIÓN CON USUARIO (Login) ---
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile', null=True, blank=True)
    # ------------------------------------
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellido")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class SalonSchedule(models.Model):
    salon = models.OneToOneField(Salon, on_delete=models.CASCADE, related_name='schedule')
    monday_open = models.BooleanField(default=True, verbose_name="Lunes")
    tuesday_open = models.BooleanField(default=True, verbose_name="Martes")
    wednesday_open = models.BooleanField(default=True, verbose_name="Miércoles")
    thursday_open = models.BooleanField(default=True, verbose_name="Jueves")
    friday_open = models.BooleanField(default=True, verbose_name="Viernes")
    saturday_open = models.BooleanField(default=True, verbose_name="Sábado")
    sunday_open = models.BooleanField(default=False, verbose_name="Domingo")

    def __str__(self):
        return f"Horario de {self.salon.name}"

# --- NUEVO: HORARIO DEL EMPLEADO ---
class EmployeeSchedule(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='schedule')
    # Guardaremos los horarios como texto simple por ahora "09:00-17:00" o "CERRADO"
    monday_hours = models.CharField(max_length=50, default="09:00-18:00", blank=True)
    tuesday_hours = models.CharField(max_length=50, default="09:00-18:00", blank=True)
    wednesday_hours = models.CharField(max_length=50, default="09:00-18:00", blank=True)
    thursday_hours = models.CharField(max_length=50, default="09:00-18:00", blank=True)
    friday_hours = models.CharField(max_length=50, default="09:00-18:00", blank=True)
    saturday_hours = models.CharField(max_length=50, default="09:00-18:00", blank=True)
    sunday_hours = models.CharField(max_length=50, default="CERRADO", blank=True)

    def __str__(self):
        return f"Horario de {self.employee}"
"""

# --- 2. ACTUALIZAR FORMS (Formulario con Usuario y Contraseña) ---
CONTENIDO_FORMS = """from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee

User = get_user_model()

class OwnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirmar")
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("password_confirm"):
            raise forms.ValidationError("Las contraseñas no coinciden.")

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'address', 'phone', 'whatsapp', 'instagram']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# --- FORMULARIO ESPECIAL DE EMPLEADO (CREA USUARIO TAMBIÉN) ---
class EmployeeCreationForm(forms.ModelForm):
    username = forms.CharField(label="Usuario de Acceso", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña Temporal", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'phone', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
"""

# --- 3. ACTUALIZAR VIEWS (Lógica de creación y Dashboards) ---
CONTENIDO_VIEWS = """from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView, ListView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from .models import Salon, Service, Employee, SalonSchedule, EmployeeSchedule
from .forms import OwnerRegistrationForm, SalonForm, ServiceForm, EmployeeForm, EmployeeCreationForm

User = get_user_model()

# --- PÚBLICO ---
def home(request):
    return render(request, 'home.html')
def marketplace(request):
    salons = Salon.objects.all()
    return render(request, 'marketplace.html', {'salons': salons})
def salon_detail(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)
    return render(request, 'salon_detail.html', {'salon': salon})
def landing_businesses(request):
    return render(request, 'landing_businesses.html')

# --- REGISTRO ---
class RegisterOwnerView(CreateView):
    template_name = 'registration/register_owner.html'
    form_class = OwnerRegistrationForm
    success_url = '/dashboard/'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context: context['user_form'] = OwnerRegistrationForm()
        if 'salon_form' not in context: context['salon_form'] = SalonForm()
        return context
    def post(self, request, *args, **kwargs):
        user_form = OwnerRegistrationForm(request.POST)
        salon_form = SalonForm(request.POST)
        if user_form.is_valid() and salon_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            salon = salon_form.save(commit=False)
            salon.owner = user
            salon.save()
            SalonSchedule.objects.create(salon=salon)
            login(request, user)
            return redirect('owner_dashboard')
        return render(request, self.template_name, {'user_form': user_form, 'salon_form': salon_form})

# --- DASHBOARDS ---
@login_required
def dashboard_redirect(request):
    # Redirige según el tipo de usuario
    if hasattr(request.user, 'salon'):
        return redirect('owner_dashboard')
    elif hasattr(request.user, 'employee_profile'):
        return redirect('employee_dashboard')
    else:
        # Cliente o Admin
        return redirect('home')

@method_decorator(login_required, name='dispatch')
class OwnerDashboardView(TemplateView):
    template_name = 'dashboard/owner_dashboard.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try: context['salon'] = self.request.user.salon
        except Salon.DoesNotExist: context['salon'] = None
        return context

@login_required
def employee_dashboard(request):
    employee = request.user.employee_profile
    return render(request, 'employee_dashboard.html', {'employee': employee})

# --- CRUD EMPLEADOS (DUEÑO) ---
@method_decorator(login_required, name='dispatch')
class OwnerEmployeesView(ListView):
    model = Employee
    template_name = 'dashboard/owner_employees.html'
    context_object_name = 'employees'
    def get_queryset(self):
        return Employee.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeCreationForm
    template_name = 'dashboard/employee_form.html'
    success_url = reverse_lazy('owner_employees')

    def form_valid(self, form):
        # 1. Crear el Usuario de Login
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        email = form.cleaned_data['email']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # 2. Crear el Perfil de Empleado
        employee = form.save(commit=False)
        employee.salon = self.request.user.salon
        employee.user = user
        employee.save()
        
        # 3. Crear Horario por defecto
        EmployeeSchedule.objects.create(employee=employee)
        
        return super().form_valid(form)

# --- SERVICIOS Y CONFIGURACIÓN ---
@method_decorator(login_required, name='dispatch')
class OwnerServicesView(ListView):
    model = Service
    template_name = 'dashboard/owner_services.html'
    context_object_name = 'services'
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class ServiceCreateView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'dashboard/service_form.html'
    success_url = reverse_lazy('owner_services')
    def form_valid(self, form):
        service = form.save(commit=False)
        service.salon = self.request.user.salon
        service.save()
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
    template_name = 'dashboard/service_confirm_delete.html'
    success_url = reverse_lazy('owner_services')
    def get_queryset(self): return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class OwnerSettingsView(UpdateView):
    model = SalonSchedule
    template_name = 'dashboard/owner_settings.html'
    fields = ['monday_open', 'tuesday_open', 'wednesday_open', 'thursday_open', 'friday_open', 'saturday_open', 'sunday_open']
    success_url = reverse_lazy('owner_settings')
    def get_object(self, queryset=None):
        salon = self.request.user.salon
        schedule, created = SalonSchedule.objects.get_or_create(salon=salon)
        return schedule
"""

# --- 4. ACTUALIZAR URLS ---
CONTENIDO_URLS = """from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Públicas
    path('', views.home, name='home'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('salon/<int:salon_id>/', views.salon_detail, name='salon_detail'),
    path('negocios/', views.landing_businesses, name='landing_businesses'),
    
    # Autenticación
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register_owner/', views.RegisterOwnerView.as_view(), name='register_owner'),

    # Redirección inteligente (Dueño vs Empleado)
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),

    # Rutas Dueño
    path('dashboard/owner/', views.OwnerDashboardView.as_view(), name='owner_dashboard'),
    path('dashboard/services/', views.OwnerServicesView.as_view(), name='owner_services'),
    path('dashboard/employees/', views.OwnerEmployeesView.as_view(), name='owner_employees'),
    path('dashboard/settings/', views.OwnerSettingsView.as_view(), name='owner_settings'),

    # Rutas Servicios
    path('dashboard/services/add/', views.ServiceCreateView.as_view(), name='service_add'),
    path('dashboard/services/edit/<int:pk>/', views.ServiceUpdateView.as_view(), name='service_edit'),
    path('dashboard/services/delete/<int:pk>/', views.ServiceDeleteView.as_view(), name='service_delete'),

    # Rutas Empleados (Dueño creando empleados)
    path('dashboard/employees/add/', views.EmployeeCreateView.as_view(), name='employee_add'),

    # Rutas Panel Empleado
    path('dashboard/employee/', views.employee_dashboard, name='employee_dashboard'),
]
"""

# --- 5. TEMPLATES DE EMPLEADOS ---
def crear_templates():
    # A. Formulario para crear empleado (owner_side)
    html_form = """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-white border-bottom">
                    <h4 class="mb-0 fw-bold">Registrar Nuevo Empleado</h4>
                </div>
                <div class="card-body p-4">
                    <form method="post">
                        {% csrf_token %}
                        
                        <h5 class="text-muted mb-3 small text-uppercase fw-bold">Datos Personales</h5>
                        <div class="row mb-3">
                            <div class="col-6">
                                <label class="form-label">Nombre</label>
                                {{ form.first_name }}
                            </div>
                            <div class="col-6">
                                <label class="form-label">Apellido</label>
                                {{ form.last_name }}
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Teléfono</label>
                            {{ form.phone }}
                        </div>
                        <div class="mb-4">
                            <label class="form-label">Email</label>
                            {{ form.email }}
                        </div>

                        <h5 class="text-muted mb-3 small text-uppercase fw-bold">Credenciales de Acceso</h5>
                        <div class="alert alert-info small">
                            Crea un usuario y contraseña para que tu empleado pueda entrar a su panel.
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Usuario</label>
                            {{ form.username }}
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Contraseña</label>
                            {{ form.password }}
                        </div>

                        <div class="d-grid gap-2 mt-4">
                            <button type="submit" class="btn btn-dark btn-lg">Registrar Empleado</button>
                            <a href="{% url 'owner_employees' %}" class="btn btn-outline-secondary">Cancelar</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
    with open(EMPLOYEE_FORM_HTML, "w", encoding="utf-8") as f:
        f.write(html_form)

    # B. Lista de Empleados (owner_side) - Actualizada con botón correcto
    owner_employees_path = os.path.join(TEMPLATES_DIR, "owner_employees.html")
    html_list = """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold text-dark">Mis Empleados</h2>
        <a href="{% url 'employee_add' %}" class="btn btn-dark">
            <i class="bi bi-person-plus-fill"></i> Nuevo Empleado
        </a>
    </div>

    <div class="card shadow-sm border-0">
        <div class="card-body p-0">
            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="bg-light">
                        <tr>
                            <th class="ps-4">Nombre</th>
                            <th>Usuario</th>
                            <th>Teléfono</th>
                            <th class="text-end pe-4">Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for employee in employees %}
                        <tr>
                            <td class="ps-4 fw-bold">{{ employee.first_name }} {{ employee.last_name }}</td>
                            <td><span class="badge bg-secondary">{{ employee.user.username }}</span></td>
                            <td>{{ employee.phone }}</td>
                            <td class="text-end pe-4">
                                <button class="btn btn-sm btn-outline-dark" title="Editar (Próximamente)"><i class="bi bi-pencil"></i></button>
                            </td>
                        </tr>
                        {% empty %}
                        <tr>
                            <td colspan="4" class="text-center py-5 text-muted">
                                <i class="bi bi-people display-4 d-block mb-3"></i>
                                No tienes empleados registrados.
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
     <div class="mt-4">
        <a href="{% url 'owner_dashboard' %}" class="text-muted text-decoration-none">
            <i class="bi bi-arrow-left"></i> Volver al Panel
        </a>
    </div>
</div>
{% endblock %}
"""
    with open(owner_employees_path, "w", encoding="utf-8") as f:
        f.write(html_list)

    # C. Dashboard del Empleado (Vista Preliminar)
    html_emp_dash = """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="d-flex justify-content-between align-items-center mb-5">
        <div>
            <h1 class="display-5 fw-bold">Hola, {{ employee.first_name }} 👋</h1>
            <p class="text-muted">Panel de Empleado - {{ employee.salon.name }}</p>
        </div>
        <form method="post" action="{% url 'logout' %}">
            {% csrf_token %}
            <button type="submit" class="btn btn-outline-danger">Cerrar Sesión</button>
        </form>
    </div>

    <div class="row g-4">
        <div class="col-md-6">
            <div class="card h-100 shadow-sm border-0 bg-dark text-white">
                <div class="card-body p-5">
                    <div class="display-1 mb-3"><i class="bi bi-calendar-week"></i></div>
                    <h3 class="card-title fw-bold">Mi Horario</h3>
                    <p class="card-text opacity-75">Configura tus horas disponibles basándote en la apertura del salón.</p>
                    <button class="btn btn-light fw-bold mt-3 disabled">Configurar (Próximamente)</button>
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="card h-100 shadow-sm border-0">
                <div class="card-body p-5">
                    <div class="display-1 mb-3 text-dark"><i class="bi bi-journal-bookmark"></i></div>
                    <h3 class="card-title fw-bold text-dark">Mis Citas</h3>
                    <p class="card-text text-muted">Revisa las reservas que tienes asignadas.</p>
                    <button class="btn btn-outline-dark fw-bold mt-3 disabled">Ver Citas (Próximamente)</button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
    with open(EMPLOYEE_DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(html_emp_dash)


def escribir_archivos():
    print("📝 1. Reescribiendo models.py (User en Empleado)...")
    with open(MODELS_PATH, "w", encoding="utf-8") as f: f.write(CONTENIDO_MODELS)
    
    print("📋 2. Reescribiendo forms.py (Formulario de Creación)...")
    with open(FORMS_PATH, "w", encoding="utf-8") as f: f.write(CONTENIDO_FORMS)

    print("🧠 3. Reescribiendo views.py (Lógica de Creación de Usuario)...")
    with open(VIEWS_PATH, "w", encoding="utf-8") as f: f.write(CONTENIDO_VIEWS)

    print("🔗 4. Reescribiendo urls.py (Nuevas rutas)...")
    with open(URLS_PATH, "w", encoding="utf-8") as f: f.write(CONTENIDO_URLS)

    print("🎨 5. Generando Templates de Empleado...")
    crear_templates()

if __name__ == "__main__":
    print("🚀 ACTIVANDO SISTEMA DE EMPLEADOS (Con Login) 🚀")
    escribir_archivos()
    print("\n✅ Archivos generados. AHORA DEBES HACER LAS MIGRACIONES.")