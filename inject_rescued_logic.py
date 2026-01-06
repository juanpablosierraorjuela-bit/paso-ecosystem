import os

# ==============================================================================
# 1. FORMULARIOS (Adaptados de Backup -> Nueva Constitución)
# ==============================================================================
# Recuperamos la capacidad de crear servicios, empleados y configurar el salón.
businesses_forms = """
from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, EmployeeSchedule

User = get_user_model()

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'buffer_time', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corte Clásico'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'buffer_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Limpieza (min)'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EmployeeCreationForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Apellido", widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(label="Celular", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        user.role = 'EMPLOYEE'
        if commit:
            user.save()
        return user

class SalonSettingsForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'description', 'address', 'city', 'deposit_percentage', 'opening_time', 'closing_time', 'maps_link', 'instagram_link']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), # Ciudad no editable fácilmente para no romper lógica
            'deposit_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'maps_link': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-control'}),
        }
"""

# ==============================================================================
# 2. VISTAS DE NEGOCIO (El Cerebro Operativo)
# ==============================================================================
# Aquí está la lógica recuperada para manejar el panel completo.
businesses_views = """
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Salon, Service, EmployeeSchedule
from apps.core.models import User, GlobalSettings
from .forms import ServiceForm, EmployeeCreationForm, SalonSettingsForm

@login_required
def owner_dashboard(request):
    if request.user.role != 'OWNER': return redirect('home')
    salon = request.user.salon
    
    # Lógica del Reaper (Pago)
    hours_since = request.user.hours_since_registration()
    hours_remaining = max(0, int(24 - hours_since))
    is_verified = request.user.is_verified_payment
    
    # Datos para el template
    context = {
        'salon': salon,
        'hours_remaining': hours_remaining,
        'is_verified': is_verified,
        'services_count': salon.services.count(),
        'employees_count': salon.staff.count(),
    }
    return render(request, 'businesses/dashboard.html', context)

@login_required
def services_list(request):
    salon = request.user.salon
    services = salon.services.all()
    
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.salon = salon
            service.save()
            messages.success(request, "Servicio creado con éxito.")
            return redirect('businesses:services')
    else:
        form = ServiceForm()
    
    return render(request, 'businesses/services.html', {'services': services, 'form': form})

@login_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk, salon=request.user.salon)
    service.delete()
    messages.success(request, "Servicio eliminado.")
    return redirect('businesses:services')

@login_required
def employees_list(request):
    salon = request.user.salon
    employees = salon.staff.all()
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.workplace = salon
            user.save()
            # Crear horario por defecto
            EmployeeSchedule.objects.create(employee=user)
            messages.success(request, "Empleado registrado.")
            return redirect('businesses:employees')
    else:
        form = EmployeeCreationForm()
        
    return render(request, 'businesses/employees.html', {'employees': employees, 'form': form})

@login_required
def settings_view(request):
    salon = request.user.salon
    if request.method == 'POST':
        form = SalonSettingsForm(request.POST, instance=salon)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración guardada.")
            return redirect('businesses:settings')
    else:
        form = SalonSettingsForm(instance=salon)
    return render(request, 'businesses/settings.html', {'form': form, 'salon': salon})
"""

# ==============================================================================
# 3. RUTAS (URLs) - Ampliadas estrictamente para gestión
# ==============================================================================
businesses_urls = """
from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    # Panel Principal
    path('dashboard/', views.owner_dashboard, name='dashboard'),
    
    # Gestión (Sub-rutas necesarias para que el dashboard funcione)
    path('servicios/', views.services_list, name='services'),
    path('servicios/eliminar/<int:pk>/', views.service_delete, name='service_delete'),
    
    path('equipo/', views.employees_list, name='employees'),
    
    path('configuracion/', views.settings_view, name='settings'),
]
"""

# ==============================================================================
# 4. TEMPLATES (Diseño Dark/Gold recuperado)
# ==============================================================================

# 4.1 Dashboard Principal (Actualizado con botones de navegación)
tpl_dashboard = """
{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="row mb-4 align-items-center">
        <div class="col">
            <h1 class="text-white fw-bold">Panel de Control</h1>
            <p class="text-secondary">{{ salon.name }}</p>
        </div>
        <div class="col-auto">
            {% if is_verified %}
                <span class="badge bg-success p-2">✅ Cuenta Verificada</span>
            {% else %}
                <span class="badge bg-warning text-dark p-2">⚠️ Pago Pendiente: {{ hours_remaining }}h restantes</span>
            {% endif %}
        </div>
    </div>

    <div class="row g-3 mb-5">
        <div class="col-md-3">
            <a href="{% url 'businesses:services' %}" class="card bg-dark border-secondary text-decoration-none h-100 hover-effect">
                <div class="card-body text-center text-white">
                    <div class="display-6 mb-2">✂️</div>
                    <h5>Servicios</h5>
                    <p class="text-muted small">{{ services_count }} Activos</p>
                </div>
            </a>
        </div>
        <div class="col-md-3">
            <a href="{% url 'businesses:employees' %}" class="card bg-dark border-secondary text-decoration-none h-100 hover-effect">
                <div class="card-body text-center text-white">
                    <div class="display-6 mb-2">👥</div>
                    <h5>Equipo</h5>
                    <p class="text-muted small">{{ employees_count }} Empleados</p>
                </div>
            </a>
        </div>
        <div class="col-md-3">
            <a href="{% url 'businesses:settings' %}" class="card bg-dark border-secondary text-decoration-none h-100 hover-effect">
                <div class="card-body text-center text-white">
                    <div class="display-6 mb-2">⚙️</div>
                    <h5>Configuración</h5>
                    <p class="text-muted small">Horarios y Datos</p>
                </div>
            </a>
        </div>
        <div class="col-md-3">
            <div class="card bg-dark border-warning h-100">
                <div class="card-body text-center text-white">
                    <div class="display-6 mb-2 text-warning">📅</div>
                    <h5 class="text-warning">Citas</h5>
                    <p class="text-muted small">Ver Agenda (Pronto)</p>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.hover-effect:hover { border-color: #d4af37 !important; transform: translateY(-5px); transition: 0.3s; }
</style>
{% endblock %}
"""

# 4.2 Servicios
tpl_services = """
{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="d-flex justify-content-between mb-4">
        <h2 class="text-white">Mis Servicios</h2>
        <a href="{% url 'businesses:dashboard' %}" class="btn btn-outline-light">Volver</a>
    </div>

    <div class="row">
        <div class="col-md-4">
            <div class="card bg-dark border-secondary p-4">
                <h5 class="text-warning mb-3">Nuevo Servicio</h5>
                <form method="post">
                    {% csrf_token %}
                    {{ form.as_p }}
                    <button type="submit" class="btn btn-warning w-100 mt-3">Guardar Servicio</button>
                </form>
            </div>
        </div>

        <div class="col-md-8">
            <div class="list-group">
                {% for service in services %}
                <div class="list-group-item bg-dark text-white border-secondary d-flex justify-content-between align-items-center">
                    <div>
                        <h5 class="mb-1 text-warning">{{ service.name }}</h5>
                        <p class="mb-0 small text-muted">{{ service.duration }} min | ${{ service.price }}</p>
                    </div>
                    <a href="{% url 'businesses:service_delete' service.id %}" class="btn btn-sm btn-danger">Eliminar</a>
                </div>
                {% empty %}
                <p class="text-white">No tienes servicios registrados.</p>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# 4.3 Empleados
tpl_employees = """
{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="d-flex justify-content-between mb-4">
        <h2 class="text-white">Mi Equipo</h2>
        <a href="{% url 'businesses:dashboard' %}" class="btn btn-outline-light">Volver</a>
    </div>

    <div class="row">
        <div class="col-md-4">
            <div class="card bg-dark border-secondary p-4">
                <h5 class="text-warning mb-3">Registrar Empleado</h5>
                <form method="post">
                    {% csrf_token %}
                    {{ form.as_p }}
                    <button type="submit" class="btn btn-warning w-100 mt-3">Crear Perfil</button>
                </form>
            </div>
        </div>

        <div class="col-md-8">
            <div class="row g-3">
                {% for emp in employees %}
                <div class="col-md-6">
                    <div class="card bg-dark border-secondary h-100">
                        <div class="card-body">
                            <h5 class="card-title text-white">{{ emp.first_name }} {{ emp.last_name }}</h5>
                            <p class="card-text text-muted small">{{ emp.email }}</p>
                            <p class="text-warning small">{{ emp.phone }}</p>
                        </div>
                    </div>
                </div>
                {% empty %}
                <p class="text-white">No hay empleados registrados.</p>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# 4.4 Configuración
tpl_settings = """
{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="d-flex justify-content-between mb-4">
        <h2 class="text-white">Configuración del Negocio</h2>
        <a href="{% url 'businesses:dashboard' %}" class="btn btn-outline-light">Volver</a>
    </div>

    <div class="card bg-dark border-secondary p-4">
        <form method="post">
            {% csrf_token %}
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="text-warning">Nombre del Negocio</label>
                    {{ form.name }}
                </div>
                <div class="col-md-6 mb-3">
                    <label class="text-warning">Ciudad (No editable)</label>
                    {{ form.city }}
                </div>
            </div>
            
            <div class="mb-3">
                <label class="text-warning">Dirección</label>
                {{ form.address }}
            </div>

            <div class="row">
                <div class="col-md-4 mb-3">
                    <label class="text-warning">Apertura</label>
                    {{ form.opening_time }}
                </div>
                <div class="col-md-4 mb-3">
                    <label class="text-warning">Cierre (Soporta madrugada)</label>
                    {{ form.closing_time }}
                </div>
                <div class="col-md-4 mb-3">
                    <label class="text-warning">% Abono</label>
                    {{ form.deposit_percentage }}
                </div>
            </div>

            <div class="mb-3">
                <label class="text-warning">Descripción (Para el Buscador Inteligente)</label>
                {{ form.description }}
            </div>

            <button type="submit" class="btn btn-warning w-100 fw-bold">GUARDAR CAMBIOS</button>
        </form>
    </div>
</div>
{% endblock %}
"""

def write_file(path, content):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"✅ Inyectado: {path}")
    except Exception as e:
        print(f"❌ Error en {path}: {e}")

if __name__ == "__main__":
    print("🚑 INICIANDO OPERACIÓN DE RESCATE Y ADAPTACIÓN...")
    
    # 1. Inyectar Forms
    write_file('apps/businesses/forms.py', businesses_forms)
    
    # 2. Inyectar Views (Lógica)
    write_file('apps/businesses/views.py', businesses_views)
    
    # 3. Inyectar URLs
    write_file('apps/businesses/urls.py', businesses_urls)
    
    # 4. Inyectar Templates
    write_file('templates/businesses/dashboard.html', tpl_dashboard)
    write_file('templates/businesses/services.html', tpl_services)
    write_file('templates/businesses/employees.html', tpl_employees)
    write_file('templates/businesses/settings.html', tpl_settings)
    
    print("\n✨ ¡Lógica recuperada y adaptada a la Constitución!")
    print("👉 EJECUTA AHORA:")
    print("   1. python manage.py makemigrations")
    print("   2. python manage.py migrate")
    print("   3. git add .")
    print("   4. git commit -m 'Rescue: Full Business Logic Adapted'")
    print("   5. git push origin main")