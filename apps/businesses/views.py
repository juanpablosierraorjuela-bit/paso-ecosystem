from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

# Modelos
from .models import Salon, OpeningHours, EmployeeSchedule, Employee, Service
# Forms
from .forms import (
    SalonForm, OpeningHoursForm, BookingForm, 
    EmployeeSettingsForm, EmployeeScheduleForm, EmployeeCreationForm,
    ServiceForm
)
# Servicios
from .services import create_booking_service
from .utils import notify_new_booking

User = get_user_model()

# --- GESTIÓN DE SERVICIOS (NUEVO) ---

@login_required
def manage_services_view(request):
    try:
        salon = request.user.salon
    except:
        return redirect('dashboard')
    
    services = salon.services.all()
    return render(request, 'dashboard/services.html', {'salon': salon, 'services': services})

@login_required
def add_service_view(request):
    try:
        salon = request.user.salon
    except:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.salon = salon
            service.save()
            messages.success(request, "Servicio creado exitosamente.")
            return redirect('manage_services')
    else:
        form = ServiceForm()
    
    return render(request, 'dashboard/service_form.html', {'form': form, 'title': 'Crear Servicio'})

@login_required
def edit_service_view(request, service_id):
    try:
        salon = request.user.salon
        service = get_object_or_404(Service, id=service_id, salon=salon)
    except:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio actualizado.")
            return redirect('manage_services')
    else:
        form = ServiceForm(instance=service)
    
    return render(request, 'dashboard/service_form.html', {'form': form, 'title': 'Editar Servicio'})

@login_required
def delete_service_view(request, service_id):
    try:
        salon = request.user.salon
        service = get_object_or_404(Service, id=service_id, salon=salon)
        service.delete()
        messages.success(request, "Servicio eliminado.")
    except:
        messages.error(request, "Error al eliminar.")
    return redirect('manage_services')

# --- EMPLEADOS Y CONFIGURACIÓN (EXISTENTE) ---

@login_required
def create_employee_view(request):
    try:
        salon = request.user.salon
    except:
        messages.error(request, "Solo los dueños de salón pueden registrar empleados.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if User.objects.filter(email=data['email']).exists():
                messages.error(request, "Este correo ya está registrado.")
            else:
                try:
                    with transaction.atomic():
                        user = User.objects.create_user(
                            username=data['email'], email=data['email'], 
                            password=data['password'], role='EMPLOYEE'
                        )
                        Employee.objects.create(salon=salon, user=user, name=data['name'], phone=data['phone'])
                    messages.success(request, f"¡Empleado {data['name']} creado!")
                    return redirect('dashboard')
                except Exception as e:
                    messages.error(request, f"Error: {e}")
    else:
        form = EmployeeCreationForm()
    return render(request, 'dashboard/create_employee.html', {'form': form, 'salon': salon})

@login_required
def salon_settings_view(request):
    salon = get_object_or_404(Salon, owner=request.user)
    if salon.opening_hours.count() < 7:
        for i in range(7):
            OpeningHours.objects.get_or_create(salon=salon, weekday=i, defaults={'from_hour': '09:00', 'to_hour': '18:00'})
            
    HoursFormSet = modelformset_factory(OpeningHours, form=OpeningHoursForm, extra=0)
    
    if request.method == 'POST':
        salon_form = SalonForm(request.POST, request.FILES, instance=salon)
        hours_formset = HoursFormSet(request.POST, queryset=salon.opening_hours.all())
        if salon_form.is_valid() and hours_formset.is_valid():
            salon_form.save(); hours_formset.save(); messages.success(request, "Configuración guardada.")
            return redirect('dashboard')
    else:
        salon_form = SalonForm(instance=salon)
        hours_formset = HoursFormSet(queryset=salon.opening_hours.all())
    return render(request, 'dashboard/settings.html', {'salon_form': salon_form, 'hours_formset': hours_formset, 'salon': salon})

@login_required
def employee_settings_view(request):
    try: employee = request.user.employee
    except: return redirect('home')
    if employee.schedules.count() < 7:
        for i in range(7): EmployeeSchedule.objects.get_or_create(employee=employee, weekday=i, defaults={'from_hour':'09:00','to_hour':'18:00'})
    ScheduleFormSet = modelformset_factory(EmployeeSchedule, form=EmployeeScheduleForm, extra=0)
    if request.method == 'POST':
        settings_form = EmployeeSettingsForm(request.POST, instance=employee)
        schedule_formset = ScheduleFormSet(request.POST, queryset=employee.schedules.all())
        if settings_form.is_valid() and schedule_formset.is_valid():
            settings_form.save(); schedule_formset.save(); messages.success(request, "Perfil actualizado.")
            return redirect('dashboard')
    else:
        settings_form = EmployeeSettingsForm(instance=employee)
        schedule_formset = ScheduleFormSet(queryset=employee.schedules.all())
    return render(request, 'dashboard/employee_dashboard.html', {'settings_form': settings_form, 'schedule_formset': schedule_formset, 'employee': employee})

def salon_detail(request, slug):
    salon = get_object_or_404(Salon, slug=slug)
    service_id = request.POST.get('service') or request.GET.get('service')
    service = None
    if service_id:
        try: service = Service.objects.get(id=service_id, salon=salon)
        except: pass

    form = BookingForm(request.POST or None, service=service)
    if request.method == 'POST' and form.is_valid():
        try:
            booking = create_booking_service(salon, service, request.user, form.cleaned_data)
            notify_new_booking(booking)
            messages.success(request, f"Reserva confirmada con {booking.employee.name if booking.employee else 'el salón'}")
            return redirect('salon_detail', slug=slug)
        except ValueError as e: messages.error(request, str(e))
        except Exception: messages.error(request, "Error inesperado")

    return render(request, 'salon_detail.html', {'salon': salon, 'form': form, 'selected_service': service})