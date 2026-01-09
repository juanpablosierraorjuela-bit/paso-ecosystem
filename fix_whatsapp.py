import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# ACTUALIZACIÓN DE VIEWS.PY (BUSINESSES)
# ==========================================
# Agregamos la librería 're' para limpiar el número y aseguramos que se use el GlobalSettings
views_content = """
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from apps.core.models import GlobalSettings, User
from .models import Service, Salon
from .forms import ServiceForm, EmployeeCreationForm, SalonScheduleForm
import re # Importante para limpiar el teléfono

# --- DASHBOARD PRINCIPAL ---
@login_required
def owner_dashboard(request):
    if request.user.role != 'OWNER':
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

    # --- LÓGICA WHATSAPP CORREGIDA ---
    admin_settings = GlobalSettings.objects.first()
    
    # 1. Obtener el número (o usar default)
    if admin_settings and admin_settings.whatsapp_support:
        raw_phone = admin_settings.whatsapp_support
    else:
        raw_phone = '573000000000' # Default si no has configurado nada
        
    # 2. PURIFICAR EL NÚMERO (Quitar espacios, +, -)
    clean_phone = re.sub(r'\D', '', str(raw_phone))
    
    # 3. Generar Link
    wa_message = f"Hola PASO, soy el negocio {salon.name} (ID {request.user.id}). Adjunto mi comprobante de pago."
    wa_link = f"https://wa.me/{clean_phone}?text={wa_message}"

    # Métricas Rápidas
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

# --- CONFIGURACIÓN DEL NEGOCIO ---
@login_required
def settings_view(request):
    salon = request.user.owned_salon
    if request.method == 'POST':
        form = SalonScheduleForm(request.POST, instance=salon)
        if form.is_valid():
            form.save()
            messages.success(request, "Horarios actualizados.")
            return redirect('settings_view')
    else:
        form = SalonScheduleForm(instance=salon)
    
    return render(request, 'businesses/settings.html', {'form': form, 'salon': salon})
"""

def fix_wa():
    print("🔧 REPARANDO LÓGICA DE WHATSAPP...")
    
    file_path = BASE_DIR / 'apps' / 'businesses' / 'views.py'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(views_content.strip())
        
    print("✅ apps/businesses/views.py actualizado.")
    print("👉 El sistema ahora limpiará automáticamente espacios y símbolos del número de soporte.")

if __name__ == "__main__":
    fix_wa()