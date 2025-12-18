from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import datetime

# Importamos formulario de usuario (Asegúrate de tener este form en apps/users/forms.py)
from apps.users.forms import CustomUserCreationForm

from apps.businesses.models import (
    Salon, Service, Booking, Employee, OpeningHours, EmployeeSchedule
)
from apps.businesses.forms import (
    SalonForm, ServiceForm, OpeningHoursForm, BookingForm, 
    EmployeeSettingsForm, EmployeeScheduleForm
)

def home(request):
    # Recuperamos todos los salones
    salons = Salon.objects.all()
    
    # Obtenemos ciudades únicas para el filtro (si lo usas en el futuro)
    ciudades = Salon.objects.values_list('city', flat=True).distinct().order_by('city')
    
    # --- CORRECCIÓN AQUÍ ---
    # Enviamos 'salons' (inglés) para que coincida con tu home.html
    return render(request, 'home.html', {
        'salons': salons,
        'ciudades': ciudades
    })

def register(request):
    if request.user.is_authenticated:
        # Redirección inteligente si ya está logueado
        if request.user.role == 'ADMIN': return redirect('dashboard')
        if request.user.role == 'EMPLOYEE': return redirect('employee_dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.first_name}!')
            
            # Redirección según rol
            if user.role == 'ADMIN': return redirect('dashboard')
            else: return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def salon_detail(request, slug):
    salon = get_object_or_404(Salon, slug=slug)
    services = salon.services.all()
    
    # Usamos la propiedad segura del modelo
    is_open = salon.is_open
    
    context = {'salon': salon, 'services': services, 'is_open': is_open}
    return render(request, 'salon_detail.html', context)

@login_required
def dashboard(request):
    # Evitar que empleados o clientes entren al panel de dueños
    if hasattr(request.user, 'role') and request.user.role in ['EMPLOYEE', 'CUSTOMER'] and not hasattr(request.user, 'salon'):
        if hasattr(request.user, 'employee'): return redirect('employee_dashboard')
        return redirect('home')

    try:
        salon = request.user.salon
    except Salon.DoesNotExist:
        # Lógica para crear salón si no existe
        if request.method == 'POST':
            form = SalonForm(request.POST)
            if form.is_valid():
                salon = form.save(commit=False)
                salon.owner = request.user
                salon.save()
                # Crear horarios por defecto (Lunes a Sábado)
                for i in range(6): 
                    OpeningHours.objects.create(salon=salon, weekday=i, from_hour=datetime.time(8,0), to_hour=datetime.time(20,0))
                # Domingo cerrado por defecto
                OpeningHours.objects.create(salon=salon, weekday=6, from_hour=datetime.time(9,0), to_hour=datetime.time(15,0), is_closed=True)
                
                messages.success(request, '¡Negocio registrado exitosamente!')
                return redirect('dashboard')
        else:
            form = SalonForm()
        return render(request, 'dashboard/create_salon.html', {'form': form})

    # Datos para el dashboard existente
    domain = request.get_host() 
    invite_link = f"http://{domain}/unete/{salon.invite_token}/"
    webhook_url = f"http://{domain}/api/webhooks/bold/"

    if request.method == 'POST':
        if 'update_settings' in request.POST:
            form = SalonForm(request.POST, request.FILES, instance=salon)
            if form.is_valid():
                form.save()
                messages.success(request, 'Información actualizada.')
                return redirect('dashboard')
        elif 'create_service' in request.POST:
            s_form = ServiceForm(request.POST)
            if s_form.is_valid():
                service = s_form.save(commit=False)
                service.salon = salon
                service.save()
                messages.success(request, 'Servicio agregado.')
                return redirect('dashboard')
        elif 'update_hours' in request.POST:
            h_form = OpeningHoursForm(request.POST)
            if h_form.is_valid():
                day = h_form.cleaned_data['weekday']
                OpeningHours.objects.update_or_create(
                    salon=salon, weekday=day,
                    defaults={
                        'from_hour': h_form.cleaned_data['from_hour'], 
                        'to_hour': h_form.cleaned_data['to_hour'], 
                        'is_closed': h_form.cleaned_data['is_closed']
                    }
                )
                messages.success(request, 'Horario actualizado.')
                return redirect('dashboard')
    else:
        form = SalonForm(instance=salon)
        s_form = ServiceForm()
        h_form = OpeningHoursForm()

    services = salon.services.all()
    bookings = salon.bookings.all().order_by('-start_time')
    employees = salon.employees.all()
    hours = salon.opening_hours.all().order_by('weekday')

    context = {
        'salon': salon, 'form': form, 's_form': s_form, 'h_form': h_form, 
        'services': services, 'bookings': bookings, 'employees': employees, 
        'hours': hours, 'invite_link': invite_link, 'webhook_url': webhook_url
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def employee_join(request, token):
    salon = get_object_or_404(Salon, invite_token=token)
    if Employee.objects.filter(user=request.user, salon=salon).exists():
        messages.info(request, 'Ya eres parte del equipo.')
        return redirect('employee_dashboard')

    if request.method == 'POST':
        employee = Employee.objects.create(user=request.user, salon=salon)
        request.user.role = 'EMPLOYEE'
        request.user.save()
        # Horario base empleado
        for i in range(5): 
            EmployeeSchedule.objects.create(employee=employee, weekday=i, from_hour=datetime.time(9,0), to_hour=datetime.time(18,0))
        messages.success(request, f'¡Bienvenido al equipo de {salon.name}!')
        return redirect('employee_dashboard')
        
    return render(request, 'registration/employee_join.html', {'salon': salon})

@login_required
def employee_dashboard(request):
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        return redirect('home')

    settings_form = EmployeeSettingsForm(instance=employee)
    schedule_form = EmployeeScheduleForm()
    
    domain = request.get_host()
    webhook_url = f"http://{domain}/api/webhooks/bold/"

    if request.method == 'POST':
        if 'update_keys' in request.POST:
            settings_form = EmployeeSettingsForm(request.POST, instance=employee)
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, 'Configuración actualizada.')
                return redirect('employee_dashboard')
        elif 'update_schedule' in request.POST:
            schedule_form = EmployeeScheduleForm(request.POST)
            if schedule_form.is_valid():
                day = schedule_form.cleaned_data['weekday']
                EmployeeSchedule.objects.update_or_create(
                    employee=employee, weekday=day,
                    defaults={'from_hour': schedule_form.cleaned_data['from_hour'], 'to_hour': schedule_form.cleaned_data['to_hour'], 'is_closed': schedule_form.cleaned_data['is_closed']}
                )
                messages.success(request, 'Horario actualizado.')
                return redirect('employee_dashboard')

    my_appointments = Booking.objects.filter(employee=employee).order_by('start_time')
    my_schedule = employee.schedule.all().order_by('weekday')

    return render(request, 'dashboard/employee_dashboard.html', {
        'employee': employee, 
        'appointments': my_appointments, 
        'my_schedule': my_schedule, 
        'settings_form': settings_form, 
        'schedule_form': schedule_form,
        'webhook_url': webhook_url
    })

def booking_create(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    salon = service.salon
    if request.method == 'POST':
        form = BookingForm(request.POST, service=service)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.service = service
            booking.salon = salon
            start_dt = booking.start_time 
            booking.end_time = start_dt + datetime.timedelta(minutes=service.duration_minutes)
            
            preferred_employee = form.cleaned_data.get('employee')
            assigned_emp = None
            if preferred_employee:
                is_free, reason = preferred_employee.is_available(start_dt.date(), start_dt.time(), service.duration_minutes)
                if is_free: assigned_emp = preferred_employee
                else: messages.error(request, f"{preferred_employee.user.first_name} no disponible: {reason}")
            else:
                for emp in salon.employees.all():
                    is_free, _ = emp.is_available(start_dt.date(), start_dt.time(), service.duration_minutes)
                    if is_free:
                        assigned_emp = emp
                        break
                if not assigned_emp: messages.error(request, "No hay disponibilidad en ese horario.")

            if assigned_emp:
                booking.employee = assigned_emp
                booking.save()
                messages.success(request, '¡Cita confirmada!')
                return redirect('booking_success')
    else:
        form = BookingForm(service=service)
    return render(request, 'booking_form.html', {'form': form, 'service': service, 'salon': salon})

def booking_success(request): return render(request, 'booking_success.html')
def api_get_availability(request): return JsonResponse({'status': 'ok'})
@csrf_exempt
def bold_webhook(request): return HttpResponse("OK")