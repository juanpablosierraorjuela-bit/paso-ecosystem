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
    SalonCreateForm, OpeningHoursForm, BookingForm, 
    EmployeeSettingsForm, EmployeeScheduleForm, EmployeeCreationForm, 
    ServiceForm
)
# Servicios
from .services import create_booking_service
from .utils import notify_new_booking

User = get_user_model()

# --- VISTAS DE DASHBOARD (Ya las tenías bien, las dejo igual por seguridad) ---

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
            email = data['email']
            password = data['password']
            name = data['name']
            phone = data['phone']

            if User.objects.filter(email=email).exists():
                messages.error(request, f"El correo {email} ya está registrado en la plataforma.")
            else:
                try:
                    with transaction.atomic():
                        user = User.objects.create_user(username=email, email=email, password=password, role='EMPLOYEE')
                        Employee.objects.create(salon=salon, user=user, name=name, phone=phone)
                    messages.success(request, f"¡Empleado {name} creado exitosamente!")
                    return redirect('dashboard')
                except Exception as e:
                    messages.error(request, f"Error creando empleado: {e}")
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
        salon_form = SalonCreateForm(request.POST, request.FILES, instance=salon)
        hours_formset = HoursFormSet(request.POST, queryset=salon.opening_hours.all())
        if salon_form.is_valid() and hours_formset.is_valid():
            salon_form.save()
            hours_formset.save()
            messages.success(request, "Configuración guardada.")
            return redirect('dashboard')
    else:
        salon_form = SalonCreateForm(instance=salon)
        hours_formset = HoursFormSet(queryset=salon.opening_hours.all())
    return render(request, 'dashboard/settings.html', {'salon_form': salon_form, 'hours_formset': hours_formset, 'salon': salon})

@login_required
def employee_settings_view(request):
    try:
        employee = request.user.employee
    except:
        messages.warning(request, "No tienes perfil de empleado.")
        return redirect('home')
    
    if employee.schedules.count() < 7:
        for i in range(7):
            EmployeeSchedule.objects.get_or_create(employee=employee, weekday=i, defaults={'from_hour': '09:00', 'to_hour': '18:00', 'is_closed': False})

    ScheduleFormSet = modelformset_factory(EmployeeSchedule, form=EmployeeScheduleForm, extra=0)

    if request.method == 'POST':
        settings_form = EmployeeSettingsForm(request.POST, instance=employee)
        schedule_formset = ScheduleFormSet(request.POST, queryset=employee.schedules.all())
        if settings_form.is_valid() and schedule_formset.is_valid():
            settings_form.save()
            schedule_formset.save()
            messages.success(request, "Perfil actualizado.")
            return redirect('dashboard')
    else:
        settings_form = EmployeeSettingsForm(instance=employee)
        schedule_formset = ScheduleFormSet(queryset=employee.schedules.all())

    return render(request, 'dashboard/employee_dashboard.html', {'settings_form': settings_form, 'schedule_formset': schedule_formset, 'employee': employee})

@login_required
def services_settings_view(request):
    try:
        salon = request.user.salon
    except:
        messages.error(request, "No tienes un salón registrado.")
        return redirect('dashboard')

    if request.method == 'POST':
        if 'create_service' in request.POST:
            form = ServiceForm(request.POST)
            if form.is_valid():
                service = form.save(commit=False)
                service.salon = salon
                service.save()
                messages.success(request, "¡Servicio agregado exitosamente!")
                return redirect('services_settings')
        elif 'delete_service' in request.POST:
            service_id = request.POST.get('service_id')
            service = get_object_or_404(Service, id=service_id, salon=salon)
            service.delete()
            messages.success(request, "Servicio eliminado.")
            return redirect('services_settings')
    else:
        form = ServiceForm()

    services = salon.services.all()
    return render(request, 'dashboard/services.html', {'salon': salon, 'form': form, 'services': services})


# --- VISTA PÚBLICA (Aquí estaba el problema) ---

def salon_detail(request, slug):
    salon = get_object_or_404(Salon, slug=slug)
    
    # 1. RECUPERAR SERVICIOS (Esto faltaba)
    services = salon.services.all()

    # 2. CALCULAR SI ESTÁ ABIERTO AHORA MISMO (Esto faltaba)
    now = timezone.localtime(timezone.now())
    current_day = now.weekday() # 0 = Lunes, 6 = Domingo
    is_open = False
    
    # Buscar el horario de hoy
    today_hours = salon.opening_hours.filter(weekday=current_day).first()
    
    if today_hours and not today_hours.is_closed:
        # Comparar hora actual con rango de apertura
        if today_hours.from_hour <= now.time() <= today_hours.to_hour:
            is_open = True

    # 3. LÓGICA DE RESERVA (Igual que antes)
    service_id = request.POST.get('service') or request.GET.get('service')
    selected_service = None
    if service_id:
        try:
            selected_service = Service.objects.get(id=service_id, salon=salon)
        except Service.DoesNotExist:
            selected_service = None

    if request.method == 'POST':
        form = BookingForm(request.POST, service=selected_service)
        if form.is_valid():
            if not selected_service:
                messages.error(request, "Selecciona un servicio.")
            else:
                try:
                    booking = create_booking_service(salon, selected_service, request.user, form.cleaned_data)
                    notify_new_booking(booking)
                    messages.success(request, f"¡Reserva confirmada con {booking.employee.name}!")
                    return redirect('salon_detail', slug=slug)
                except ValueError as e:
                    messages.error(request, str(e))
                except Exception as e:
                    messages.error(request, "Error inesperado.")
    else:
        form = BookingForm(service=selected_service)

    return render(request, 'salon_detail.html', {
        'salon': salon, 
        'form': form, 
        'selected_service': selected_service,
        'services': services,  # Enviamos los servicios a la plantilla
        'is_open': is_open     # Enviamos el estado real (Abierto/Cerrado)
    })