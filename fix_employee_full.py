import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. ACTUALIZAR REDIRECCIÓN (CORE VIEWS)
# ==========================================
def fix_dispatch():
    views_path = BASE_DIR / 'apps' / 'core' / 'views.py'
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Cambiamos la redirección del empleado
    if "return redirect('employees_list')" in content:
        content = content.replace(
            "return redirect('employees_list')",
            "return redirect('employee_dashboard')  # CORREGIDO: Panel del Empleado"
        )
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ apps/core/views.py: Redirección de empleado corregida.")
    else:
        print("ℹ️ Redirección ya estaba correcta o no encontrada.")

# ==========================================
# 2. MEJORAR DASHBOARD EMPLEADO (VIEWS BUSINESSES)
# ==========================================
# Necesitamos agregar la lógica para editar el perfil del empleado (User)
# y proteger la vista de lista de empleados.

views_businesses_content = """
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from apps.core.models import GlobalSettings, User
from .models import Service, Salon, EmployeeSchedule
from .forms import ServiceForm, EmployeeCreationForm, SalonScheduleForm, OwnerUpdateForm, SalonUpdateForm, EmployeeScheduleUpdateForm
import re

# --- DASHBOARD PRINCIPAL (SOLO DUEÑOS) ---
@login_required
def owner_dashboard(request):
    if request.user.role != 'OWNER':
        # Si entra un empleado aquí, lo mandamos a SU panel
        if request.user.role == 'EMPLOYEE':
            return redirect('employee_dashboard')
        return redirect('home')
    
    try:
        salon = request.user.owned_salon
    except:
        return redirect('register_owner')

    # Lógica Timer
    elapsed_time = timezone.now() - request.user.registration_timestamp
    time_limit = timedelta(hours=24)
    remaining_time = time_limit - elapsed_time
    total_seconds_left = max(0, int(remaining_time.total_seconds()))

    # Lógica WhatsApp
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

# --- GESTIÓN DE SERVICIOS (SOLO DUEÑOS) ---
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
            messages.success(request, "Servicio creado exitosamente.")
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

# --- GESTIÓN DE EMPLEADOS (SOLO DUEÑOS) ---
@login_required
def employees_list(request):
    if request.user.role != 'OWNER': return redirect('home')
    
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
    if request.user.role != 'OWNER': return redirect('home')
    employee = get_object_or_404(User, pk=pk, workplace=request.user.owned_salon)
    employee.delete()
    messages.success(request, "Empleado eliminado.")
    return redirect('employees_list')

# --- CONFIGURACIÓN DEL NEGOCIO (SOLO DUEÑOS) ---
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

# --- PANEL DEL EMPLEADO (MI AGENDA) ---
@login_required
def employee_dashboard(request):
    if request.user.role != 'EMPLOYEE':
        return redirect('dashboard')
    
    schedule, created = EmployeeSchedule.objects.get_or_create(employee=request.user)
    
    # Manejo de Dos Formularios: Horario y Perfil
    schedule_form = EmployeeScheduleUpdateForm(instance=schedule)
    profile_form = OwnerUpdateForm(instance=request.user) # Reusamos el form de Owner que tiene los campos basicos

    if request.method == 'POST':
        if 'update_schedule' in request.POST:
            schedule_form = EmployeeScheduleUpdateForm(request.POST, instance=schedule)
            if schedule_form.is_valid():
                schedule_form.save()
                messages.success(request, "Tu disponibilidad ha sido actualizada.")
                return redirect('employee_dashboard')
        
        elif 'update_profile' in request.POST:
            profile_form = OwnerUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Tus datos personales han sido actualizados.")
                return redirect('employee_dashboard')
    
    return render(request, 'businesses/employee_dashboard.html', {
        'schedule_form': schedule_form,
        'profile_form': profile_form,
        'schedule': schedule,
        'salon': request.user.workplace
    })
"""

# ==========================================
# 3. ACTUALIZAR TEMPLATE EMPLEADO
# ==========================================
# Agregamos la sección de "Mis Datos" al dashboard del empleado
html_employee_dash = """
{% extends 'base.html' %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    
    <div class="flex justify-between items-center mb-8 border-b pb-4">
        <div>
            <h1 class="text-3xl font-serif font-bold text-gray-900">Hola, {{ user.first_name }}</h1>
            <p class="text-gray-500">Talento en <strong>{{ salon.name }}</strong></p>
        </div>
        <div class="text-right">
            <span class="bg-black text-white text-xs font-bold px-3 py-1 rounded-full">
                PANEL EMPLEADO
            </span>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <div class="lg:col-span-1 space-y-8">
            
            <div class="bg-white p-6 rounded-xl shadow border border-gray-100">
                <h2 class="text-xl font-bold mb-4 flex items-center">
                    ⏰ Mi Disponibilidad
                </h2>
                <form method="post">
                    {% csrf_token %}
                    
                    <div class="bg-gray-50 p-3 rounded-lg mb-4">
                        <label class="text-xs font-bold text-gray-400 uppercase">Jornada Laboral</label>
                        <div class="grid grid-cols-2 gap-2 mt-2">
                            <div>
                                <span class="text-xs text-gray-600">Entrada</span>
                                {{ schedule_form.work_start }}
                            </div>
                            <div>
                                <span class="text-xs text-gray-600">Salida</span>
                                {{ schedule_form.work_end }}
                            </div>
                        </div>
                    </div>

                    <div class="bg-gray-50 p-3 rounded-lg mb-4">
                        <label class="text-xs font-bold text-gray-400 uppercase">Hora de Almuerzo</label>
                        <div class="grid grid-cols-2 gap-2 mt-2">
                            <div>
                                <span class="text-xs text-gray-600">Inicio</span>
                                {{ schedule_form.lunch_start }}
                            </div>
                            <div>
                                <span class="text-xs text-gray-600">Fin</span>
                                {{ schedule_form.lunch_end }}
                            </div>
                        </div>
                    </div>

                    <div class="mb-6">
                        <label class="text-xs font-bold text-gray-400 uppercase block mb-2">Días Activos</label>
                        <div class="grid grid-cols-2 gap-2 text-sm">
                            {% for checkbox in schedule_form.active_days %}
                            <label class="flex items-center space-x-2 cursor-pointer">
                                {{ checkbox.tag }}
                                <span>{{ checkbox.choice_label }}</span>
                            </label>
                            {% endfor %}
                        </div>
                    </div>

                    <button type="submit" name="update_schedule" class="w-full bg-black text-white py-3 rounded-lg font-bold hover:bg-gray-800 transition">
                        Actualizar Horario
                    </button>
                </form>
            </div>

            <div class="bg-white p-6 rounded-xl shadow border border-gray-100">
                <h2 class="text-xl font-bold mb-4 flex items-center">
                    👤 Mis Datos
                </h2>
                <form method="post">
                    {% csrf_token %}
                    <div class="space-y-3 mb-4">
                        <div>
                            <label class="text-xs font-bold text-gray-500">Nombre</label>
                            {{ profile_form.first_name }}
                        </div>
                        <div>
                            <label class="text-xs font-bold text-gray-500">Apellido</label>
                            {{ profile_form.last_name }}
                        </div>
                        <div>
                            <label class="text-xs font-bold text-gray-500">WhatsApp (Para notificaciones)</label>
                            {{ profile_form.phone }}
                        </div>
                        <div>
                            <label class="text-xs font-bold text-gray-500">Email</label>
                            {{ profile_form.email }}
                        </div>
                    </div>
                    <button type="submit" name="update_profile" class="w-full bg-white border border-gray-300 text-gray-700 py-2 rounded-lg font-bold hover:bg-gray-50 transition text-sm">
                        Guardar Perfil
                    </button>
                </form>
            </div>

        </div>

        <div class="lg:col-span-2">
            <div class="bg-white p-6 rounded-xl shadow border border-gray-100 min-h-[400px]">
                <h2 class="text-xl font-bold mb-6">📅 Mis Citas Confirmadas</h2>
                
                <div class="text-center py-12 bg-gray-50 rounded-xl border-dashed border-2 border-gray-200">
                    <div class="text-4xl mb-3">📭</div>
                    <p class="text-gray-500 font-medium">No tienes citas verificadas para hoy.</p>
                    <p class="text-xs text-gray-400 mt-2">Las citas aparecerán aquí cuando el dueño confirme el pago.</p>
                </div>
            </div>
        </div>

    </div>
</div>

<style>
    input[type="time"] { width: 100%; padding: 4px; border: 1px solid #e5e7eb; border-radius: 4px; }
</style>
{% endblock %}
"""

def apply_fix():
    print("🔧 AJUSTANDO ROLES DE EMPLEADO...")
    
    # 1. Dispatch
    fix_dispatch()
    
    # 2. Views
    with open(BASE_DIR / 'apps' / 'businesses' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(views_businesses_content.strip())
    print("✅ apps/businesses/views.py: Vistas protegidas y perfil de empleado agregado.")

    # 3. Template
    with open(BASE_DIR / 'templates' / 'businesses' / 'employee_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_employee_dash.strip())
    print("✅ templates/businesses/employee_dashboard.html: Interfaz actualizada.")

if __name__ == "__main__":
    apply_fix()
    print("\n🚀 LISTO. Ahora el empleado tiene su propio espacio y no choca con el dueño.")