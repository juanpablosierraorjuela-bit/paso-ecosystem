from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, time
from apps.core.models import GlobalSettings, User
from apps.marketplace.models import Appointment
from .models import Service, Salon, EmployeeSchedule
from .forms import (
    ServiceForm, EmployeeCreationForm, SalonScheduleForm, 
    OwnerUpdateForm, SalonUpdateForm, EmployeeScheduleUpdateForm
)
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

    # Lógica de tiempo restante para el pago (24h)
    elapsed_time = timezone.now() - request.user.registration_timestamp
    time_limit = timedelta(hours=24)
    remaining_time = time_limit - elapsed_time
    total_seconds_left = max(0, int(remaining_time.total_seconds()))

    # Configuración de soporte de WhatsApp
    admin_settings = GlobalSettings.objects.first()
    raw_phone = admin_settings.whatsapp_support if (admin_settings and admin_settings.whatsapp_support) else '573000000000'
    clean_phone = re.sub(r'\D', '', str(raw_phone))
    if not clean_phone.startswith('57'): 
        clean_phone = '57' + clean_phone
    
    wa_support_link = f"https://wa.me/{clean_phone}?text=Hola,%20necesito%20verificar%20mi%20pago%20para%20{salon.name}"

    # Citas para verificar (pendientes)
    pending_appointments = Appointment.objects.filter(salon=salon, status='PENDING').order_by('-created_at')

    return render(request, 'businesses/owner_dashboard.html', {
        'salon': salon,
        'seconds_left': total_seconds_left,
        'wa_support_link': wa_support_link,
        'pending_appointments': pending_appointments,
        'is_verified': request.user.is_verified_payment
    })

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
            messages.success(request, "Servicio creado con éxito.")
            return redirect('services_list')
    else:
        form = ServiceForm()
        
    return render(request, 'businesses/services_list.html', {
        'services': services,
        'form': form
    })

@login_required
def service_edit(request, pk):
    if request.user.role != 'OWNER': return redirect('home')
    service = get_object_or_404(Service, pk=pk, salon__owner=request.user)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio actualizado.")
            return redirect('services_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'businesses/service_form.html', {'form': form, 'edit': True})

@login_required
def service_delete(request, pk):
    if request.user.role != 'OWNER': return redirect('home')
    service = get_object_or_404(Service, pk=pk, salon__owner=request.user)
    service.delete()
    messages.success(request, "Servicio eliminado correctamente.")
    return redirect('services_list')

@login_required
def employees_list(request):
    if request.user.role != 'OWNER': return redirect('home')
    salon = request.user.owned_salon
    employees = User.objects.filter(workplace=salon, role='EMPLOYEE')
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.role = 'EMPLOYEE'
            employee.workplace = salon
            employee.set_password(form.cleaned_data['password'])
            employee.save()
            
            # Crear horario inicial por defecto
            EmployeeSchedule.objects.get_or_create(employee=employee)
            
            messages.success(request, f"Empleado {employee.username} registrado.")
            return redirect('employees_list')
    else:
        form = EmployeeCreationForm()
        
    return render(request, 'businesses/employees_list.html', {
        'employees': employees,
        'form': form
    })

@login_required
def employee_delete(request, pk):
    if request.user.role != 'OWNER': return redirect('home')
    employee = get_object_or_404(User, pk=pk, workplace__owner=request.user, role='EMPLOYEE')
    employee.delete()
    messages.success(request, "Empleado eliminado del equipo.")
    return redirect('employees_list')

@login_required
def settings_view(request):
    if request.user.role != 'OWNER': return redirect('home')
    salon = request.user.owned_salon
    
    owner_form = OwnerUpdateForm(instance=request.user)
    salon_form = SalonUpdateForm(instance=salon)
    
    if request.method == 'POST':
        if 'update_owner' in request.POST:
            owner_form = OwnerUpdateForm(request.POST, instance=request.user)
            if owner_form.is_valid():
                owner_form.save()
                messages.success(request, "Datos personales actualizados.")
                return redirect('settings_view')
        elif 'update_salon' in request.POST:
            salon_form = SalonUpdateForm(request.POST, instance=salon)
            if salon_form.is_valid():
                salon_form.save()
                messages.success(request, "Datos del negocio actualizados.")
                return redirect('settings_view')

    return render(request, 'businesses/settings.html', {
        'owner_form': owner_form, 
        'salon_form': salon_form,
        'salon': salon
    })

@login_required
def employee_dashboard(request):
    if request.user.role != 'EMPLOYEE': return redirect('dashboard')
    
    schedule, created = EmployeeSchedule.objects.get_or_create(
        employee=request.user, 
        defaults={'work_start': time(9,0), 'work_end': time(18,0)}
    )
    
    # Citas verificadas para el empleado actual
    appointments = Appointment.objects.filter(
        employee=request.user,
        status='VERIFIED'
    ).order_by('date_time')
    
    for app in appointments:
        app.balance_due = app.total_price - app.deposit_amount

    schedule_form = EmployeeScheduleUpdateForm(instance=schedule)
    profile_form = OwnerUpdateForm(instance=request.user)

    if request.method == 'POST':
        if 'update_schedule' in request.POST:
            schedule_form = EmployeeScheduleUpdateForm(request.POST, instance=schedule)
            if schedule_form.is_valid():
                schedule_form.save()
                messages.success(request, "Disponibilidad de horario actualizada.")
                return redirect('employee_dashboard')
        elif 'update_profile' in request.POST:
            profile_form = OwnerUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Perfil de empleado actualizado.")
                return redirect('employee_dashboard')
    
    return render(request, 'businesses/employee_dashboard.html', {
        'schedule_form': schedule_form,
        'profile_form': profile_form,
        'schedule': schedule,
        'appointments': appointments
    })

@login_required
def verify_appointment(request, appointment_id):
    if request.user.role != 'OWNER': return redirect('home')
    appointment = get_object_or_404(Appointment, id=appointment_id, salon__owner=request.user)
    appointment.status = 'VERIFIED'
    appointment.save()
    messages.success(request, f"La cita de {appointment.client.first_name} ha sido marcada como VERIFICADA.")
    return redirect('dashboard')