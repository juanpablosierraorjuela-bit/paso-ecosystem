import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. ACTUALIZAR BUSINESSES VIEWS (LOGICA DE VERIFICACIÓN)
# ==========================================
views_content = """
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from apps.core.models import GlobalSettings, User
from apps.marketplace.models import Appointment
from .models import Service, Salon, EmployeeSchedule
from .forms import ServiceForm, EmployeeCreationForm, SalonScheduleForm, OwnerUpdateForm, SalonUpdateForm, EmployeeScheduleUpdateForm
import re

@login_required
def owner_dashboard(request):
    if request.user.role != 'OWNER':
        if request.user.role == 'EMPLOYEE':
            return redirect('employee_dashboard')
        return redirect('home')
    
    try:
        salon = request.user.owned_salon
    except:
        return redirect('register_owner')

    # --- LÓGICA TIMER ---
    elapsed_time = timezone.now() - request.user.registration_timestamp
    time_limit = timedelta(hours=24)
    remaining_time = time_limit - elapsed_time
    total_seconds_left = max(0, int(remaining_time.total_seconds()))

    # --- LÓGICA WHATSAPP ACTIVACIÓN ---
    admin_settings = GlobalSettings.objects.first()
    raw_phone = admin_settings.whatsapp_support if (admin_settings and admin_settings.whatsapp_support) else '573000000000'
    clean_phone = re.sub(r'\D', '', str(raw_phone))
    if not clean_phone.startswith('57'): clean_phone = '57' + clean_phone
        
    wa_message = f"Hola PASO, soy el negocio {salon.name} (ID {request.user.id}). Adjunto mi comprobante de pago."
    wa_link = f"https://wa.me/{clean_phone}?text={wa_message}"

    # --- LÓGICA DE CITAS (NUEVO) ---
    # Traemos todas las citas ordenadas por fecha (las más recientes primero)
    appointments = Appointment.objects.filter(salon=salon).order_by('-date_time')
    
    # Calculamos saldo pendiente para cada una
    for app in appointments:
        app.balance_due = app.total_price - app.deposit_amount

    context = {
        'salon': salon,
        'appointments': appointments, # <--- AQUI ESTAN LAS CITAS
        'seconds_left': total_seconds_left,
        'wa_link': wa_link,
        'is_trial': not request.user.is_verified_payment,
        'service_count': salon.services.count(),
        'employee_count': salon.employees.count(),
    }
    return render(request, 'businesses/dashboard.html', context)

# --- ACCIÓN VERIFICAR CITA (NUEVO) ---
@login_required
def verify_appointment(request, appointment_id):
    salon = request.user.owned_salon
    # Aseguramos que la cita pertenezca a ESTE salón para seguridad
    appointment = get_object_or_404(Appointment, id=appointment_id, salon=salon)
    
    if appointment.status == 'PENDING':
        appointment.status = 'CONFIRMED'
        appointment.save()
        messages.success(request, f"Cita de {appointment.client.first_name} verificada correctamente.")
    
    return redirect('dashboard')

# --- OTRAS VISTAS (Mantenemos igual) ---
@login_required
def services_list(request):
    if request.user.role != 'OWNER': return redirect('home')
    salon = request.user.owned_salon
    services = salon.services.all()
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.salon = salon
            service.save()
            messages.success(request, "Servicio creado.")
            return redirect('services_list')
    else:
        form = ServiceForm()
    return render(request, 'businesses/services.html', {'services': services, 'form': form})

@login_required
def service_delete(request, pk):
    if request.user.role != 'OWNER': return redirect('home')
    service = get_object_or_404(Service, pk=pk, salon=request.user.owned_salon)
    service.delete()
    messages.success(request, "Servicio eliminado.")
    return redirect('services_list')

@login_required
def employees_list(request):
    if request.user.role != 'OWNER': return redirect('home')
    salon = request.user.owned_salon
    employees = salon.employees.all()
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone'],
                role='EMPLOYEE',
                workplace=salon,
                is_verified_payment=True
            )
            messages.success(request, "Empleado creado.")
            return redirect('employees_list')
    else:
        form = EmployeeCreationForm()
    return render(request, 'businesses/employees.html', {'employees': employees, 'form': form})

@login_required
def employee_delete(request, pk):
    if request.user.role != 'OWNER': return redirect('home')
    employee = get_object_or_404(User, pk=pk, workplace=request.user.owned_salon)
    employee.delete()
    messages.success(request, "Empleado eliminado.")
    return redirect('employees_list')

@login_required
def settings_view(request):
    if request.user.role != 'OWNER': return redirect('home')
    salon = request.user.owned_salon
    user = request.user
    owner_form = OwnerUpdateForm(instance=user)
    salon_form = SalonUpdateForm(instance=salon)
    schedule_form = SalonScheduleForm(instance=salon)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            owner_form = OwnerUpdateForm(request.POST, instance=user)
            salon_form = SalonUpdateForm(request.POST, instance=salon)
            if owner_form.is_valid() and salon_form.is_valid():
                owner_form.save()
                salon_form.save()
                messages.success(request, "Datos actualizados.")
                return redirect('settings_view')
        elif 'update_schedule' in request.POST:
            schedule_form = SalonScheduleForm(request.POST, instance=salon)
            if schedule_form.is_valid():
                schedule_form.save()
                messages.success(request, "Horarios actualizados.")
                return redirect('settings_view')

    return render(request, 'businesses/settings.html', {
        'owner_form': owner_form, 
        'salon_form': salon_form,
        'schedule_form': schedule_form,
        'salon': salon
    })

@login_required
def employee_dashboard(request):
    if request.user.role != 'EMPLOYEE': return redirect('dashboard')
    schedule, created = EmployeeSchedule.objects.get_or_create(employee=request.user)
    schedule_form = EmployeeScheduleUpdateForm(instance=schedule)
    profile_form = OwnerUpdateForm(instance=request.user)

    if request.method == 'POST':
        if 'update_schedule' in request.POST:
            schedule_form = EmployeeScheduleUpdateForm(request.POST, instance=schedule)
            if schedule_form.is_valid():
                schedule_form.save()
                messages.success(request, "Disponibilidad actualizada.")
                return redirect('employee_dashboard')
        elif 'update_profile' in request.POST:
            profile_form = OwnerUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Perfil actualizado.")
                return redirect('employee_dashboard')
    
    return render(request, 'businesses/employee_dashboard.html', {
        'schedule_form': schedule_form,
        'profile_form': profile_form,
        'schedule': schedule,
        'salon': request.user.workplace
    })
"""

# ==========================================
# 2. ACTUALIZAR BUSINESSES URLS (RUTA DE VERIFICACIÓN)
# ==========================================
urls_content = """
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.owner_dashboard, name='dashboard'),
    path('servicios/', views.services_list, name='services_list'),
    path('servicios/eliminar/<int:pk>/', views.service_delete, name='service_delete'),
    path('equipo/', views.employees_list, name='employees_list'),
    path('equipo/eliminar/<int:pk>/', views.employee_delete, name='employee_delete'),
    path('configuracion/', views.settings_view, name='settings_view'),
    path('mi-agenda/', views.employee_dashboard, name='employee_dashboard'),
    
    # --- NUEVA RUTA VERIFICAR ---
    path('cita/verificar/<int:appointment_id>/', views.verify_appointment, name='verify_appointment'),
]
"""

# ==========================================
# 3. ACTUALIZAR DASHBOARD TEMPLATE (TABLA DE CITAS)
# ==========================================
html_dashboard = """
{% extends 'base.html' %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    
    <div class="flex flex-col md:flex-row justify-between items-center mb-8 border-b pb-4">
        <div>
            <h1 class="text-3xl font-serif font-bold text-gray-900">Panel de Control</h1>
            <p class="text-gray-500">Bienvenido, {{ user.first_name }}</p>
        </div>
        
        {% if is_trial %}
        <div class="mt-4 md:mt-0 bg-red-50 border border-red-200 px-4 py-3 rounded-lg flex items-center">
            <div class="mr-3 text-red-500">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            </div>
            <div>
                <p class="text-xs font-bold text-red-800 uppercase">Cuenta en Riesgo</p>
                <p class="text-sm font-mono font-bold text-red-600" id="countdown">--:--:--</p>
            </div>
            <a href="{{ wa_link }}" target="_blank" class="ml-4 bg-red-600 text-white text-xs font-bold px-3 py-2 rounded hover:bg-red-700 transition">
                Pagar Ahora
            </a>
        </div>
        {% else %}
        <div class="mt-4 md:mt-0 bg-green-50 border border-green-200 px-4 py-3 rounded-lg flex items-center">
            <span class="text-green-600 text-2xl mr-2">✅</span>
            <div>
                <p class="text-sm font-bold text-green-800">Cuenta Verificada</p>
                <p class="text-xs text-green-600">Suscripción Activa</p>
            </div>
        </div>
        {% endif %}
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        <div class="lg:col-span-1 space-y-4">
            <div class="bg-white p-6 rounded-xl shadow border border-gray-100">
                <h3 class="font-bold text-gray-400 text-xs uppercase mb-4">Gestión</h3>
                <nav class="space-y-2">
                    <a href="{% url 'services_list' %}" class="flex justify-between items-center px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg group transition">
                        <span>💇‍♀️ Servicios</span>
                        <span class="bg-gray-100 text-gray-600 text-xs font-bold px-2 py-0.5 rounded group-hover:bg-white">{{ service_count }}</span>
                    </a>
                    <a href="{% url 'employees_list' %}" class="flex justify-between items-center px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg group transition">
                        <span>👥 Equipo</span>
                        <span class="bg-gray-100 text-gray-600 text-xs font-bold px-2 py-0.5 rounded group-hover:bg-white">{{ employee_count }}</span>
                    </a>
                    <a href="{% url 'settings_view' %}" class="block px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg transition">
                        ⚙️ Configuración
                    </a>
                </nav>
            </div>
        </div>

        <div class="lg:col-span-3">
            <div class="bg-white rounded-xl shadow border border-gray-100 overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                    <h2 class="font-bold text-gray-800">📅 Agenda de Citas</h2>
                    <span class="text-xs text-gray-500">Ordenado por más reciente</span>
                </div>

                {% if appointments %}
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm text-gray-600">
                        <thead class="bg-gray-50 text-xs uppercase font-bold text-gray-500">
                            <tr>
                                <th class="px-6 py-3">Fecha/Hora</th>
                                <th class="px-6 py-3">Cliente</th>
                                <th class="px-6 py-3">Servicio</th>
                                <th class="px-6 py-3">Estado</th>
                                <th class="px-6 py-3">Saldo</th>
                                <th class="px-6 py-3 text-right">Acción</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100">
                            {% for app in appointments %}
                            <tr class="hover:bg-gray-50 transition">
                                <td class="px-6 py-4 font-mono text-xs">
                                    {{ app.date_time|date:"d M, Y" }}<br>
                                    <span class="text-gray-900 font-bold text-sm">{{ app.date_time|date:"h:i A" }}</span>
                                </td>
                                <td class="px-6 py-4">
                                    <div class="font-bold text-gray-900">{{ app.client.first_name }} {{ app.client.last_name }}</div>
                                    <div class="text-xs text-gray-400">{{ app.client.phone }}</div>
                                </td>
                                <td class="px-6 py-4">
                                    {{ app.service.name }}<br>
                                    <span class="text-xs text-gray-400">con {{ app.employee.first_name }}</span>
                                </td>
                                <td class="px-6 py-4">
                                    {% if app.status == 'PENDING' %}
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                            ⏳ Pendiente
                                        </span>
                                    {% elif app.status == 'CONFIRMED' %}
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                            ✅ Confirmada
                                        </span>
                                    {% endif %}
                                </td>
                                <td class="px-6 py-4 font-bold text-gray-900">
                                    ${{ app.balance_due }}
                                </td>
                                <td class="px-6 py-4 text-right">
                                    {% if app.status == 'PENDING' %}
                                    <a href="{% url 'verify_appointment' app.id %}" class="bg-black text-white text-xs font-bold px-3 py-2 rounded hover:bg-gray-800 transition shadow-lg">
                                        Verificar Abono
                                    </a>
                                    {% else %}
                                    <span class="text-gray-300 text-xs">---</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="text-center py-12">
                    <div class="text-4xl mb-2">📭</div>
                    <p class="text-gray-500">Aún no tienes citas agendadas.</p>
                </div>
                {% endif %}
            </div>
        </div>

    </div>
</div>

<script>
    // Script para el contador de la cuenta del dueño
    (function() {
        let seconds = {{ seconds_left }};
        const timerEl = document.getElementById('countdown');
        if (timerEl) {
            const interval = setInterval(() => {
                if (seconds <= 0) {
                    clearInterval(interval);
                    timerEl.innerText = "EXPIRADO";
                    return;
                }
                let h = Math.floor(seconds / 3600);
                let m = Math.floor((seconds % 3600) / 60);
                let s = seconds % 60;
                timerEl.innerText = `${h}:${m < 10 ? '0'+m : m}:${s < 10 ? '0'+s : s}`;
                seconds--;
            }, 1000);
        }
    })();
</script>
{% endblock %}
"""

def apply_upgrade():
    print("🚀 INSTALANDO GESTOR DE CITAS EN DASHBOARD DUEÑO...")
    
    # 1. Views
    with open(BASE_DIR / 'apps' / 'businesses' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(views_content.strip())
    print("✅ apps/businesses/views.py: Lógica de listado y verificación añadida.")

    # 2. URLs
    with open(BASE_DIR / 'apps' / 'businesses' / 'urls.py', 'w', encoding='utf-8') as f:
        f.write(urls_content.strip())
    print("✅ apps/businesses/urls.py: Ruta de verificación conectada.")

    # 3. Template
    with open(BASE_DIR / 'templates' / 'businesses' / 'dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_dashboard.strip())
    print("✅ templates/businesses/dashboard.html: Tabla de citas implementada.")

if __name__ == "__main__":
    apply_upgrade()