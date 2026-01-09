import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. ACTUALIZAR FORMS.PY (NUEVOS FORMULARIOS)
# ==========================================
forms_content = """
from django import forms
from .models import Service, Salon
from apps.core.models import User

# Lista de ciudades para mantener la consistencia
COLOMBIA_CITIES = [
    ('Bogotá D.C.', 'Bogotá D.C.'), ('Medellín', 'Medellín'), ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'), ('Cartagena', 'Cartagena'), ('Bucaramanga', 'Bucaramanga'),
    ('Manizales', 'Manizales'), ('Pereira', 'Pereira'), ('Cúcuta', 'Cúcuta'),
    ('Ibagué', 'Ibagué'), ('Santa Marta', 'Santa Marta'), ('Villavicencio', 'Villavicencio'),
    ('Pasto', 'Pasto'), ('Tunja', 'Tunja'), ('Montería', 'Montería'),
    ('Valledupar', 'Valledupar'), ('Armenia', 'Armenia'), ('Neiva', 'Neiva'),
    ('Popayán', 'Popayán'), ('Sincelejo', 'Sincelejo'), ('Riohacha', 'Riohacha'),
    ('Zipaquirá', 'Zipaquirá'), ('Soacha', 'Soacha'), ('Envigado', 'Envigado'),
    ('Itagüí', 'Itagüí'), ('Bello', 'Bello'), ('Otro', 'Otro (Escribir en dirección)'),
]

# --- ACTUALIZAR DATOS DUEÑO ---
class OwnerUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'phone': 'WhatsApp Personal',
            'email': 'Correo Electrónico'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- ACTUALIZAR DATOS NEGOCIO ---
class SalonUpdateForm(forms.ModelForm):
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad Base")

    class Meta:
        model = Salon
        fields = ['name', 'address', 'city', 'instagram_url', 'google_maps_url']
        labels = {
            'name': 'Nombre del Negocio',
            'address': 'Dirección Física',
            'instagram_url': 'Link Instagram',
            'google_maps_url': 'Link Google Maps'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'
            
# --- SERVICIOS ---
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'duration_minutes', 'price', 'buffer_time']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- EMPLEADOS ---
class EmployeeCreationForm(forms.ModelForm):
    username = forms.CharField(label="Usuario de Acceso", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña", required=True)
    first_name = forms.CharField(label="Nombre", required=True)
    last_name = forms.CharField(label="Apellido", required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- HORARIOS ---
class SalonScheduleForm(forms.ModelForm):
    opening_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Apertura")
    closing_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Cierre")

    class Meta:
        model = Salon
        fields = ['opening_time', 'closing_time', 'deposit_percentage']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'
"""

# ==========================================
# 2. ACTUALIZAR VIEWS.PY (LOGICA MULTI-FORM)
# ==========================================
# Mantenemos las otras vistas iguales, solo actualizamos settings_view
# Para no borrar todo el archivo, leeremos y reemplazaremos solo imports y la vista settings_view
# Pero para evitar errores de parseo, reescribiremos el archivo completo con la lógica nueva integrada.

views_content = """
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from apps.core.models import GlobalSettings, User
from .models import Service, Salon
from .forms import ServiceForm, EmployeeCreationForm, SalonScheduleForm, OwnerUpdateForm, SalonUpdateForm
import re

# --- DASHBOARD PRINCIPAL ---
@login_required
def owner_dashboard(request):
    if request.user.role != 'OWNER':
        return redirect('home')
    
    try:
        salon = request.user.owned_salon
    except:
        return redirect('register_owner')

    elapsed_time = timezone.now() - request.user.registration_timestamp
    time_limit = timedelta(hours=24)
    remaining_time = time_limit - elapsed_time
    total_seconds_left = max(0, int(remaining_time.total_seconds()))

    admin_settings = GlobalSettings.objects.first()
    if admin_settings and admin_settings.whatsapp_support:
        raw_phone = admin_settings.whatsapp_support
    else:
        raw_phone = '573000000000'
        
    clean_phone = re.sub(r'\D', '', str(raw_phone))
    wa_message = f"Hola PASO, soy el negocio {salon.name} (ID {request.user.id}). Adjunto mi comprobante de pago."
    wa_link = f"https://wa.me/{clean_phone}?text={wa_message}"

    service_count = salon.services.count()
    employee_count = salon.employees.count()

    context = {
        'salon': salon,
        'seconds_left': total_seconds_left,
        'wa_link': wa_link,
        'is_trial': not request.user.is_verified_payment,
        'service_count': service_count,
        'employee_count': employee_count,
    }
    return render(request, 'businesses/dashboard.html', context)

# --- GESTIÓN DE SERVICIOS ---
@login_required
def services_list(request):
    salon = request.user.owned_salon
    services = salon.services.all()
    
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.salon = salon
            service.save()
            messages.success(request, "Servicio creado exitosamente.")
            return redirect('services_list')
    else:
        form = ServiceForm()

    return render(request, 'businesses/services.html', {'services': services, 'form': form})

@login_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk, salon=request.user.owned_salon)
    service.delete()
    messages.success(request, "Servicio eliminado.")
    return redirect('services_list')

# --- GESTIÓN DE EMPLEADOS ---
@login_required
def employees_list(request):
    salon = request.user.owned_salon
    employees = salon.employees.all()
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone'],
                role='EMPLOYEE',
                workplace=salon,
                is_verified_payment=True
            )
            messages.success(request, f"Empleado {user.first_name} creado.")
            return redirect('employees_list')
    else:
        form = EmployeeCreationForm()

    return render(request, 'businesses/employees.html', {'employees': employees, 'form': form})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(User, pk=pk, workplace=request.user.owned_salon)
    employee.delete()
    messages.success(request, "Empleado eliminado.")
    return redirect('employees_list')

# --- CONFIGURACIÓN TOTAL (NUEVA LÓGICA) ---
@login_required
def settings_view(request):
    salon = request.user.owned_salon
    user = request.user

    # Formularios iniciales
    owner_form = OwnerUpdateForm(instance=user)
    salon_form = SalonUpdateForm(instance=salon)
    schedule_form = SalonScheduleForm(instance=salon)

    if request.method == 'POST':
        # Distinguir qué formulario se envió usando el 'name' del botón submit
        
        if 'update_profile' in request.POST:
            owner_form = OwnerUpdateForm(request.POST, instance=user)
            salon_form = SalonUpdateForm(request.POST, instance=salon)
            if owner_form.is_valid() and salon_form.is_valid():
                owner_form.save()
                salon_form.save()
                messages.success(request, "Datos de perfil y negocio actualizados.")
                return redirect('settings_view')
                
        elif 'update_schedule' in request.POST:
            schedule_form = SalonScheduleForm(request.POST, instance=salon)
            if schedule_form.is_valid():
                schedule_form.save()
                messages.success(request, "Horarios y reglas de pago actualizados.")
                return redirect('settings_view')

    return render(request, 'businesses/settings.html', {
        'owner_form': owner_form, 
        'salon_form': salon_form,
        'schedule_form': schedule_form,
        'salon': salon
    })
"""

# ==========================================
# 3. TEMPLATE MEJORADO (SETTINGS.HTML)
# ==========================================
html_settings = """
{% extends 'base.html' %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    
    <div class="flex justify-between items-center mb-8 border-b pb-4">
        <div>
            <h1 class="text-3xl font-serif font-bold text-gray-900">Configuración del Ecosistema</h1>
            <p class="text-gray-500 text-sm">Gestiona tu identidad y tus reglas de operación.</p>
        </div>
        <a href="{% url 'dashboard' %}" class="text-sm font-bold text-gray-600 hover:text-black">&larr; Volver al Panel</a>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-10">
        
        <div>
            <div class="bg-white p-8 rounded-xl shadow border border-gray-100 mb-8">
                <h2 class="text-xl font-bold mb-6 flex items-center">
                    <span class="bg-black text-white w-8 h-8 rounded-full flex items-center justify-center mr-3 text-sm">1</span>
                    Datos de Identidad
                </h2>
                
                <form method="post">
                    {% csrf_token %}
                    
                    <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Información del Dueño</h3>
                    <div class="grid grid-cols-2 gap-4 mb-4">
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">Nombre</label>
                            {{ owner_form.first_name }}
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">Apellido</label>
                            {{ owner_form.last_name }}
                        </div>
                    </div>
                    <div class="mb-4">
                        <label class="block text-xs font-medium text-gray-700 mb-1">WhatsApp</label>
                        {{ owner_form.phone }}
                    </div>
                    <div class="mb-6">
                        <label class="block text-xs font-medium text-gray-700 mb-1">Email</label>
                        {{ owner_form.email }}
                    </div>

                    <hr class="border-gray-100 my-6">

                    <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Información del Negocio</h3>
                    <div class="mb-4">
                        <label class="block text-xs font-medium text-gray-700 mb-1">Nombre del Salón</label>
                        {{ salon_form.name }}
                    </div>
                    <div class="mb-4">
                        <label class="block text-xs font-medium text-gray-700 mb-1">Ciudad</label>
                        {{ salon_form.city }}
                    </div>
                    <div class="mb-4">
                        <label class="block text-xs font-medium text-gray-700 mb-1">Dirección</label>
                        {{ salon_form.address }}
                    </div>
                    <div class="grid grid-cols-2 gap-4 mb-6">
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">Instagram URL</label>
                            {{ salon_form.instagram_url }}
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-1">Maps URL</label>
                            {{ salon_form.google_maps_url }}
                        </div>
                    </div>

                    <button type="submit" name="update_profile" class="w-full bg-gray-900 text-white py-3 rounded-lg font-bold hover:bg-black transition shadow-lg">
                        Guardar Identidad
                    </button>
                </form>
            </div>
        </div>

        <div>
            <div class="bg-white p-8 rounded-xl shadow border border-gray-100">
                <h2 class="text-xl font-bold mb-6 flex items-center">
                    <span class="bg-black text-white w-8 h-8 rounded-full flex items-center justify-center mr-3 text-sm">2</span>
                    Reglas de Operación
                </h2>
                
                <form method="post">
                    {% csrf_token %}
                    
                    <div class="bg-gray-50 p-4 rounded-lg mb-6 border border-gray-200">
                        <p class="text-sm text-gray-600 mb-2"><strong>Horario Global:</strong> Define cuándo abres y cierras.</p>
                        <p class="text-xs text-gray-500 italic">* Si el cierre es menor que la apertura (ej: 10pm a 4am), el sistema entenderá que es amanecida.</p>
                    </div>

                    <div class="grid grid-cols-2 gap-6 mb-6">
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-2">Hora Apertura</label>
                            {{ schedule_form.opening_time }}
                        </div>
                        <div>
                            <label class="block text-xs font-medium text-gray-700 mb-2">Hora Cierre</label>
                            {{ schedule_form.closing_time }}
                        </div>
                    </div>

                    <hr class="border-gray-100 my-6">

                    <div class="mb-6">
                        <label class="block text-xs font-medium text-gray-700 mb-2">Porcentaje de Abono (%)</label>
                        {{ schedule_form.deposit_percentage }}
                        <p class="text-xs text-gray-500 mt-2">
                            El cliente debe pagar este % del servicio por adelantado para que la cita se confirme.
                        </p>
                    </div>

                    <button type="submit" name="update_schedule" class="w-full bg-white text-black border-2 border-black py-3 rounded-lg font-bold hover:bg-gray-50 transition">
                        Actualizar Reglas
                    </button>
                </form>
            </div>
        </div>

    </div>
</div>
{% endblock %}
"""

# ==========================================
# 4. EJECUCIÓN
# ==========================================
def apply_upgrade():
    print("🛠️  MEJORANDO PANEL DE CONFIGURACIÓN...")

    # 1. Forms
    with open(BASE_DIR / 'apps' / 'businesses' / 'forms.py', 'w', encoding='utf-8') as f:
        f.write(forms_content.strip())
    print("✅ apps/businesses/forms.py: Formularios de Perfil agregados.")

    # 2. Views
    with open(BASE_DIR / 'apps' / 'businesses' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(views_content.strip())
    print("✅ apps/businesses/views.py: Lógica Multi-Form implementada.")

    # 3. Template
    with open(BASE_DIR / 'templates' / 'businesses' / 'settings.html', 'w', encoding='utf-8') as f:
        f.write(html_settings.strip())
    print("✅ templates/businesses/settings.html: Interfaz de Lujo creada.")

if __name__ == "__main__":
    apply_upgrade()
    print("\n🚀 LISTO. Ahora puedes editar todo: Tu nombre, el nombre del salón, redes, horarios, etc.")