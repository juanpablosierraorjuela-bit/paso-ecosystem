from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, time # Importación corregida aquí
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

    elapsed_time = timezone.now() - request.user.registration_timestamp
    time_limit = timedelta(hours=24)
    remaining_time = time_limit - elapsed_time
    total_seconds_left = max(0, int(remaining_time.total_seconds()))

    admin_settings = GlobalSettings.objects.first()
    raw_phone = admin_settings.whatsapp_support if (admin_settings and admin_settings.whatsapp_support) else '573000000000'
    clean_phone = re.sub(r'\D', '', str(raw_phone))
    if not clean_phone.startswith('57'): clean_phone = '57' + clean_phone
        
    wa_message = f"Hola PASO, soy el negocio {salon.name} (ID {request.user.id}). Adjunto mi comprobante de pago."
    wa_link = f"https://wa.me/{clean_phone}?text={wa_message}"

    appointments = Appointment.objects.filter(salon=salon).order_by('-date_time')
    
    for app in appointments:
        app.balance_due = app.total_price - app.deposit_amount

    context = {
        'salon': salon,
        'appointments': appointments,
        'seconds_left': total_seconds_left,
        'wa_link': wa_link,
        'is_trial': not request.user.is_verified_payment,
        'service_count': salon.services.count(),
        'employee_count': salon.employees.count(),
    }
    return render(request, 'businesses/dashboard.html', context)

@login_required
def verify_appointment(request, appointment_id):
    salon = request.user.owned_salon
    appointment = get_object_or_404(Appointment, id=appointment_id, salon=salon)
    if appointment.status == 'PENDING':
        appointment.status = 'CONFIRMED'
        appointment.save()
        messages.success(request, f"Cita de {appointment.client.first_name} verificada correctamente.")
    return redirect('dashboard')

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
def service_edit(request, pk):
    if request.user.role != 'OWNER': return redirect('home')
    service = get_object_or_404(Service, pk=pk, salon=request.user.owned_salon)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio actualizado correctamente.")
            return redirect('services_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'businesses/service_edit.html', {'form': form, 'service': service})

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
    
    schedule, created = EmployeeSchedule.objects.get_or_create(
        employee=request.user, 
        defaults={'work_start': time(9,0), 'work_end': time(18,0)}
    )
    
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