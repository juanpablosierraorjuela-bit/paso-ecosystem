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