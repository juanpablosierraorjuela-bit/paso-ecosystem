from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import datetime
import uuid

# --- IMPORTACIONES CORREGIDAS ---
from apps.users.forms import CustomUserCreationForm
from apps.businesses.models import (
    Salon, Service, Booking, Employee, OpeningHours, EmployeeSchedule
)
from apps.businesses.forms import (
    SalonForm, ServiceForm, OpeningHoursForm, BookingForm, 
    EmployeeSettingsForm, EmployeeScheduleForm
)

def home(request):
    salons = Salon.objects.all()
    # Usamos set() para evitar duplicados y sorted para ordenar
    ciudades = sorted(list(set(Salon.objects.values_list('city', flat=True))))
    return render(request, 'home.html', {'salons': salons, 'ciudades': ciudades})

def register(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'role', 'CUSTOMER') == 'ADMIN': return redirect('dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.first_name}!')
            if getattr(user, 'role', 'CUSTOMER') == 'ADMIN': return redirect('dashboard')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def salon_detail(request, slug):
    salon = get_object_or_404(Salon, slug=slug)
    services = salon.services.all()
    is_open = getattr(salon, 'is_open', False)
    return render(request, 'salon_detail.html', {'salon': salon, 'services': services, 'is_open': is_open})

@login_required
def dashboard(request):
    # 1. Seguridad
    if getattr(request.user, 'role', 'CUSTOMER') != 'ADMIN':
        if getattr(request.user, 'role', 'CUSTOMER') == 'EMPLOYEE': return redirect('employee_dashboard')
        return redirect('home')

    # 2. Obtener o Crear Salón
    try:
        salon = request.user.salon
    except Exception:
        if request.method == 'POST':
            form = SalonForm(request.POST, request.FILES)
            if form.is_valid():
                salon = form.save(commit=False)
                salon.owner = request.user
                salon.save()
                for i in range(6): OpeningHours.objects.create(salon=salon, weekday=i, from_hour=datetime.time(8,0), to_hour=datetime.time(20,0))
                OpeningHours.objects.create(salon=salon, weekday=6, from_hour=datetime.time(9,0), to_hour=datetime.time(15,0), is_closed=True)
                messages.success(request, '¡Negocio creado!')
                return redirect('dashboard')
        else:
            form = SalonForm()
        return render(request, 'dashboard/create_salon.html', {'form': form})

    # 3. Inicializar Forms (Evita error 500)
    form = SalonForm(instance=salon)
    s_form = ServiceForm()
    h_form = OpeningHoursForm()

    if request.method == 'POST':
        if 'update_settings' in request.POST:
            form = SalonForm(request.POST, request.FILES, instance=salon)
            if form.is_valid():
                form.save()
                messages.success(request, 'Guardado.')
                return redirect('dashboard')
        elif 'create_service' in request.POST:
            s_form = ServiceForm(request.POST)
            if s_form.is_valid():
                srv = s_form.save(commit=False)
                srv.salon = salon
                srv.save()
                messages.success(request, 'Servicio creado.')
                return redirect('dashboard')
        elif 'update_hours' in request.POST:
            h_form = OpeningHoursForm(request.POST)
            if h_form.is_valid():
                day = h_form.cleaned_data['weekday']
                OpeningHours.objects.update_or_create(salon=salon, weekday=day, defaults={'from_hour': h_form.cleaned_data['from_hour'], 'to_hour': h_form.cleaned_data['to_hour'], 'is_closed': h_form.cleaned_data['is_closed']})
                messages.success(request, 'Horario actualizado.')
                return redirect('dashboard')

    # 4. Contexto Seguro
    try:
        if not salon.invite_token:
            salon.invite_token = uuid.uuid4()
            salon.save(update_fields=['invite_token'])
        invite_link = f"http://{request.get_host()}/unete/{salon.invite_token}/"
    except:
        invite_link = "#"

    return render(request, 'dashboard/index.html', {
        'salon': salon, 'form': form, 's_form': s_form, 'h_form': h_form,
        'services': salon.services.all(), 'bookings': salon.bookings.all().order_by('-start_time'),
        'employees': salon.employees.all(), 'hours': salon.opening_hours.all().order_by('weekday'),
        'invite_link': invite_link, 'webhook_url': f"http://{request.get_host()}/api/webhooks/bold/"
    })

@login_required
def employee_join(request, token):
    salon = get_object_or_404(Salon, invite_token=token)
    if Employee.objects.filter(user=request.user, salon=salon).exists(): return redirect('employee_dashboard')
    if request.method == 'POST':
        employee = Employee.objects.create(user=request.user, salon=salon)
        request.user.role = 'EMPLOYEE'
        request.user.save()
        for i in range(5): EmployeeSchedule.objects.create(employee=employee, weekday=i, from_hour=datetime.time(9,0), to_hour=datetime.time(18,0))
        messages.success(request, '¡Bienvenido!')
        return redirect('employee_dashboard')
    return render(request, 'registration/employee_join.html', {'salon': salon})

@login_required
def employee_dashboard(request):
    try: employee = request.user.employee
    except: return redirect('home')
    settings_form = EmployeeSettingsForm(instance=employee)
    schedule_form = EmployeeScheduleForm()
    if request.method == 'POST':
        if 'update_keys' in request.POST:
            settings_form = EmployeeSettingsForm(request.POST, instance=employee)
            if settings_form.is_valid(): settings_form.save(); messages.success(request, 'Guardado.'); return redirect('employee_dashboard')
        elif 'update_schedule' in request.POST:
            schedule_form = EmployeeScheduleForm(request.POST)
            if schedule_form.is_valid():
                EmployeeSchedule.objects.update_or_create(employee=employee, weekday=schedule_form.cleaned_data['weekday'], defaults={'from_hour': schedule_form.cleaned_data['from_hour'], 'to_hour': schedule_form.cleaned_data['to_hour'], 'is_closed': schedule_form.cleaned_data['is_closed']})
                messages.success(request, 'Actualizado.')
                return redirect('employee_dashboard')
    return render(request, 'dashboard/employee_dashboard.html', {'employee': employee, 'appointments': Booking.objects.filter(employee=employee).order_by('start_time'), 'my_schedule': employee.schedule.all().order_by('weekday'), 'settings_form': settings_form, 'schedule_form': schedule_form})

def booking_create(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = BookingForm(request.POST, service=service)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.service = service
            booking.salon = service.salon
            booking.end_time = booking.start_time + datetime.timedelta(minutes=service.duration_minutes)
            if form.cleaned_data.get('employee'): booking.employee = form.cleaned_data['employee']
            else: booking.employee = service.salon.employees.first()
            booking.save()
            return redirect('booking_success')
    else: form = BookingForm(service=service)
    return render(request, 'booking_form.html', {'form': form, 'service': service})

def booking_success(request): return render(request, 'booking_success.html')
def api_get_availability(request): return JsonResponse({'status': 'ok'})
@csrf_exempt
def bold_webhook(request): return HttpResponse("OK")
