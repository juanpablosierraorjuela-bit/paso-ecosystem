import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. ACTUALIZAR CORE VIEWS (PAGO DE ABONO DEL CLIENTE)
# ==========================================
core_views_content = """
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from apps.businesses.forms import OwnerRegistrationForm
from apps.businesses.models import Salon
from apps.core.models import User, GlobalSettings
from apps.marketplace.models import Appointment
import re

def home(request):
    return render(request, 'home.html')

def register_owner(request):
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = OwnerRegistrationForm()
    return render(request, 'registration/register_owner.html', {'form': form})

def login_view(request):
    pass

@login_required
def dispatch_user(request):
    user = request.user
    if user.role == 'OWNER':
        return redirect('dashboard')
    elif user.role == 'CLIENT':
        return redirect('marketplace_home')
    elif user.role == 'EMPLOYEE':
        return redirect('employee_dashboard')
    elif user.is_superuser:
        return redirect('/admin/')
    else:
        return redirect('home')

@login_required
def client_dashboard(request):
    appointments = Appointment.objects.filter(client=request.user).order_by('-created_at')
    
    for app in appointments:
        if app.status == 'PENDING':
            elapsed = timezone.now() - app.created_at
            remaining = timedelta(minutes=60) - elapsed
            app.seconds_left = max(0, int(remaining.total_seconds()))
            
            # --- CORRECCIÓN WHATSAPP COLOMBIA ---
            try:
                owner_phone = app.salon.owner.phone
                if owner_phone:
                    # Limpiar todo lo que no sea número
                    clean_phone = re.sub(r'\D', '', str(owner_phone))
                    # Si no empieza por 57, se lo pegamos
                    if not clean_phone.startswith('57'):
                        clean_phone = '57' + clean_phone
                else:
                    clean_phone = '573000000000'
            except:
                clean_phone = '573000000000'
            
            msg = (
                f"Hola {app.salon.name}, soy {request.user.first_name}. "
                f"Confirmo mi cita para {app.service.name} el {app.date_time.strftime('%d/%m %I:%M %p')}. "
                f"Adjunto abono de ${int(app.deposit_amount)}."
            )
            app.wa_link = f"https://wa.me/{clean_phone}?text={msg}"
            
    return render(request, 'core/client_dashboard.html', {'appointments': appointments})
"""

# ==========================================
# 2. ACTUALIZAR BUSINESSES VIEWS (ACTIVACIÓN DE CUENTA DUEÑO)
# ==========================================
businesses_views_content = """
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from apps.core.models import GlobalSettings, User
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

    elapsed_time = timezone.now() - request.user.registration_timestamp
    time_limit = timedelta(hours=24)
    remaining_time = time_limit - elapsed_time
    total_seconds_left = max(0, int(remaining_time.total_seconds()))

    admin_settings = GlobalSettings.objects.first()
    if admin_settings and admin_settings.whatsapp_support:
        raw_phone = admin_settings.whatsapp_support
    else:
        raw_phone = '573000000000'
        
    # --- CORRECCIÓN WHATSAPP COLOMBIA (DUEÑO -> ADMIN) ---
    clean_phone = re.sub(r'\D', '', str(raw_phone))
    if not clean_phone.startswith('57'):
        clean_phone = '57' + clean_phone
        
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
    if request.user.role != 'EMPLOYEE':
        return redirect('dashboard')
    
    schedule, created = EmployeeSchedule.objects.get_or_create(employee=request.user)
    schedule_form = EmployeeScheduleUpdateForm(instance=schedule)
    profile_form = OwnerUpdateForm(instance=request.user)

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

def apply_fix_57():
    print("🇨🇴 APLICANDO PARCHE COLOMBIA (+57) A WHATSAPP...")
    
    # 1. Core Views (Cliente -> Dueño)
    with open(BASE_DIR / 'apps' / 'core' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(core_views_content.strip())
    print("✅ apps/core/views.py: Botón de abono actualizado con 57.")

    # 2. Businesses Views (Dueño -> Admin)
    with open(BASE_DIR / 'apps' / 'businesses' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(businesses_views_content.strip())
    print("✅ apps/businesses/views.py: Botón de activación actualizado con 57.")

if __name__ == "__main__":
    apply_fix_57()