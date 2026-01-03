import os
import sys
import subprocess

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Archivos a modificar
VIEWS_PATH = os.path.join(APP_DIR, "views.py")
URLS_PATH = os.path.join(APP_DIR, "urls.py")
MODELS_PATH = os.path.join(APP_DIR, "models.py")
MARKETPLACE_HTML = os.path.join(TEMPLATES_DIR, "marketplace.html")
DASHBOARD_HTML = os.path.join(TEMPLATES_DIR, "dashboard", "owner_dashboard.html")
SETTINGS_HTML = os.path.join(TEMPLATES_DIR, "dashboard", "owner_settings.html")

# --- 1. MODELOS: Asegurar la estructura de Horarios (Schedule) ---
def actualizar_modelos():
    print("🔧 1. Verificando Modelos (Horarios)...")
    with open(MODELS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Nos aseguramos de tener un modelo SalonSchedule simple si no existe
    if "class SalonSchedule(models.Model):" not in content:
        print("   -> Agregando modelo de Horarios al archivo...")
        nuevo_modelo = """
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
"""
        with open(MODELS_PATH, "a", encoding="utf-8") as f:
            f.write(nuevo_modelo)
    else:
        print("   -> El modelo de horarios ya existe.")

# --- 2. VISTAS: Arreglar Redirección y crear Vistas del Dashboard ---
def actualizar_views():
    print("code 2. Actualizando Vistas (Redirección y Dashboard)...")
    
    # Reescribimos views.py para asegurar que todo esté conectado y limpio
    # IMPORTANTE: Mantenemos la lógica de registro que ya funcionaba
    
    contenido_views = """from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView, ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from django.urls import reverse_lazy
from .models import Salon, Service, Employee, SalonSchedule
from .forms import OwnerRegistrationForm, SalonForm, ServiceForm, EmployeeForm

# --- PÚBLICO ---

def home(request):
    return render(request, 'home.html')

def marketplace(request):
    salons = Salon.objects.all()
    return render(request, 'marketplace.html', {'salons': salons})

def salon_detail(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)
    return render(request, 'salon_detail.html', {'salon': salon})

# --- REGISTRO (ARREGLADO: Redirige al Dashboard) ---

class RegisterOwnerView(CreateView):
    template_name = 'registration/register_owner.html'
    form_class = OwnerRegistrationForm
    success_url = '/dashboard/'  # <--- AQUÍ ESTÁ EL CAMBIO CLAVE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = OwnerRegistrationForm()
        if 'salon_form' not in context:
            context['salon_form'] = SalonForm()
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
            
            # Crear horario por defecto
            SalonSchedule.objects.create(salon=salon)
            
            login(request, user)
            return redirect('owner_dashboard') # Redirección explícita
        
        return render(request, self.template_name, {
            'user_form': user_form,
            'salon_form': salon_form
        })

# --- PANEL DE DUEÑO (DASHBOARD) ---

@method_decorator(login_required, name='dispatch')
class OwnerDashboardView(TemplateView):
    template_name = 'dashboard/owner_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Intentar obtener el salón del usuario actual
        try:
            context['salon'] = self.request.user.salon
        except Salon.DoesNotExist:
            context['salon'] = None
        return context

@method_decorator(login_required, name='dispatch')
class OwnerServicesView(ListView):
    model = Service
    template_name = 'dashboard/owner_services.html'
    context_object_name = 'services'

    def get_queryset(self):
        return Service.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class OwnerEmployeesView(ListView):
    model = Employee
    template_name = 'dashboard/owner_employees.html'
    context_object_name = 'employees'

    def get_queryset(self):
        return Employee.objects.filter(salon__owner=self.request.user)

@method_decorator(login_required, name='dispatch')
class OwnerSettingsView(UpdateView):
    model = SalonSchedule
    template_name = 'dashboard/owner_settings.html'
    fields = ['monday_open', 'tuesday_open', 'wednesday_open', 'thursday_open', 'friday_open', 'saturday_open', 'sunday_open']
    success_url = reverse_lazy('owner_settings')

    def get_object(self, queryset=None):
        # Obtiene o crea el horario del salón del usuario
        salon = self.request.user.salon
        schedule, created = SalonSchedule.objects.get_or_create(salon=salon)
        return schedule
"""
    with open(VIEWS_PATH, "w", encoding="utf-8") as f:
        f.write(contenido_views)

# --- 3. URLS: Conectar los botones ---
def actualizar_urls():
    print("🔗 3. Conectando URLs del Dashboard...")
    contenido_urls = """from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Públicas
    path('', views.home, name='home'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('salon/<int:salon_id>/', views.salon_detail, name='salon_detail'),
    
    # Autenticación
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register_owner/', views.RegisterOwnerView.as_view(), name='register_owner'),

    # Dashboard Dueño (Aquí arreglamos los botones caídos)
    path('dashboard/', views.OwnerDashboardView.as_view(), name='owner_dashboard'),
    path('dashboard/services/', views.OwnerServicesView.as_view(), name='owner_services'),
    path('dashboard/employees/', views.OwnerEmployeesView.as_view(), name='owner_employees'),
    path('dashboard/settings/', views.OwnerSettingsView.as_view(), name='owner_settings'),
]
"""
    with open(URLS_PATH, "w", encoding="utf-8") as f:
        f.write(contenido_urls)

# --- 4. TEMPLATE MARKETPLACE: Agregar Íconos ---
def arreglar_marketplace():
    print("🛍️ 4. Agregando íconos al Marketplace...")
    
    # Sobrescribimos con una versión que incluye la lógica de íconos
    contenido_marketplace = """{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="container py-5">
    <div class="text-center mb-5">
        <h1 class="display-4 fw-bold text-dark">Explora Negocios Exclusivos</h1>
        <p class="lead text-muted">Encuentra los mejores servicios de belleza cerca de ti.</p>
    </div>

    <div class="row row-cols-1 row-cols-md-3 g-4">
        {% for salon in salons %}
        <div class="col">
            <div class="card h-100 shadow-sm border-0 hover-effect">
                <div class="bg-dark text-white d-flex align-items-center justify-content-center" style="height: 200px;">
                    <i class="bi bi-shop display-1 text-white-50"></i>
                </div>
                
                <div class="card-body">
                    <h5 class="card-title fw-bold">{{ salon.name }}</h5>
                    <p class="card-text text-muted small">{{ salon.description|truncatewords:20 }}</p>
                    
                    <div class="d-flex gap-2 mb-3">
                        {% if salon.address %}
                        <span class="badge bg-light text-dark border" title="{{ salon.address }}">
                            <i class="bi bi-geo-alt-fill text-danger"></i>
                        </span>
                        {% endif %}
                        
                        {% if salon.whatsapp %}
                        <a href="https://wa.me/{{ salon.whatsapp }}" target="_blank" class="btn btn-sm btn-success rounded-circle" title="WhatsApp">
                            <i class="bi bi-whatsapp"></i>
                        </a>
                        {% endif %}
                        
                        {% if salon.instagram %}
                        <a href="https://instagram.com/{{ salon.instagram }}" target="_blank" class="btn btn-sm btn-danger rounded-circle" style="background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); border:none;" title="Instagram">
                            <i class="bi bi-instagram"></i>
                        </a>
                        {% endif %}
                    </div>
                </div>
                <div class="card-footer bg-white border-top-0">
                    <a href="{% url 'salon_detail' salon.id %}" class="btn btn-dark w-100">Ver Servicios y Reservar</a>
                </div>
            </div>
        </div>
        {% empty %}
        <div class="col-12 text-center">
            <p class="text-muted">Aún no hay negocios registrados.</p>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""
    with open(MARKETPLACE_HTML, "w", encoding="utf-8") as f:
        f.write(contenido_marketplace)

# --- 5. TEMPLATE SETTINGS: Configuración de Días ---
def crear_template_settings():
    print("⚙️ 5. Creando panel de Configuración de Horarios...")
    # Aseguramos que la carpeta exista
    os.makedirs(os.path.dirname(SETTINGS_HTML), exist_ok=True)
    
    contenido_settings = """{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="row">
        <div class="col-md-3 mb-4">
            <div class="list-group">
                <a href="{% url 'owner_dashboard' %}" class="list-group-item list-group-item-action">Resumen</a>
                <a href="{% url 'owner_services' %}" class="list-group-item list-group-item-action">Servicios</a>
                <a href="{% url 'owner_employees' %}" class="list-group-item list-group-item-action">Empleados</a>
                <a href="{% url 'owner_settings' %}" class="list-group-item list-group-item-action active bg-dark border-dark">Configuración</a>
            </div>
        </div>
        
        <div class="col-md-9">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-white border-bottom">
                    <h4 class="mb-0">Días de Apertura del Negocio</h4>
                </div>
                <div class="card-body">
                    <p class="text-muted mb-4">Selecciona los días que tu negocio abre. Tus empleados solo podrán configurar horarios en estos días.</p>
                    
                    <form method="post">
                        {% csrf_token %}
                        <div class="row g-3">
                            {% for field in form %}
                            <div class="col-md-4">
                                <div class="form-check form-switch p-3 border rounded">
                                    {{ field }}
                                    <label class="form-check-label fw-bold ms-2" for="{{ field.id_for_label }}">
                                        {{ field.label }}
                                    </label>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        <div class="mt-4">
                            <button type="submit" class="btn btn-dark">Guardar Configuración</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
    with open(SETTINGS_HTML, "w", encoding="utf-8") as f:
        f.write(contenido_settings)

# --- 6. MIGRACIONES ---
def ejecutar_migraciones():
    print("💾 6. Actualizando base de datos...")
    try:
        subprocess.run([sys.executable, "manage.py", "makemigrations"], check=True)
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print("✅ Base de datos lista.")
    except Exception as e:
        print(f"⚠️ Nota: Si hubo error, intenta correr 'python manage.py makemigrations' manualmente.")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    print("🚀 INICIANDO REPARACIÓN FUNCIONAL...")
    actualizar_modelos()
    actualizar_views()
    actualizar_urls()
    arreglar_marketplace()
    crear_template_settings()
    ejecutar_migraciones()
    print("\n✅ ¡LISTO! Ahora prueba:")
    print("1. Registrar un nuevo dueño -> Debería llevarte al Dashboard.")
    print("2. Ir al Marketplace -> Deberías ver los íconos de WhatsApp/Instagram.")
    print("3. En el Dashboard -> El botón Configuración te deja elegir los días.")