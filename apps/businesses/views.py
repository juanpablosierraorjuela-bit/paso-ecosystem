from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import JsonResponse
import datetime

# Modelos
from .models import Salon, OpeningHours, EmployeeSchedule, Employee, Service, Booking
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

# --- API: OBTENER HORAS DISPONIBLES (NUEVO) ---
def get_available_slots(request):
    employee_id = request.GET.get('employee_id')
    service_id = request.GET.get('service_id')
    date_str = request.GET.get('date')

    if not (employee_id and service_id and date_str):
        return JsonResponse({'error': 'Faltan datos'}, status=400)

    try:
        employee = Employee.objects.get(id=employee_id)
        service = Service.objects.get(id=service_id)
        query_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # 1. Determinar horario base (Del empleado o del salón)
        # Por defecto 9am a 6pm si no hay configuración
        start_hour = datetime.time(9, 0)
        end_hour = datetime.time(18, 0)
        
        # Buscar horario específico del empleado para ese día
        weekday = query_date.weekday()
        schedule = employee.schedules.filter(weekday=weekday).first()
        
        if schedule:
            if schedule.is_closed:
                return JsonResponse({'slots': []}) # Cerrado hoy
            start_hour = schedule.from_hour
            end_hour = schedule.to_hour
        else:
            # Si el empleado no tiene horario propio, usar el del salón
            salon_hours = employee.salon.opening_hours.filter(weekday=weekday).first()
            if salon_hours:
                if salon_hours.is_closed:
                    return JsonResponse({'slots': []})
                start_hour = salon_hours.from_hour
                end_hour = salon_hours.to_hour

        # 2. Generar todos los slots posibles (cada 30 min)
        slots = []
        current_time = datetime.datetime.combine(query_date, start_hour)
        end_time = datetime.datetime.combine(query_date, end_hour)
        
        # Obtener reservas existentes de ese día
        bookings = Booking.objects.filter(
            employee=employee,
            start_time__date=query_date
        )

        while current_time + datetime.timedelta(minutes=service.duration_minutes) <= end_time:
            slot_start = current_time
            slot_end = current_time + datetime.timedelta(minutes=service.duration_minutes)
            is_available = True

            # Verificar si choca con alguna reserva existente
            # Lógica: (SlotInicia < ReservaTermina) Y (SlotTermina > ReservaInicia)
            for booking in bookings:
                booking_end = booking.start_time + datetime.timedelta(minutes=booking.service.duration_minutes)
                # Convertir booking.start_time a naive si es necesario para comparar
                b_start = timezone.make_naive(booking.start_time) if timezone.is_aware(booking.start_time) else booking.start_time
                b_end = timezone.make_naive(booking_end) if timezone.is_aware(booking_end) else booking_end

                if slot_start < b_end and slot_end > b_start:
                    is_available = False
                    break
            
            # Verificar si ya pasó la hora (si es hoy)
            if query_date == timezone.localdate() and slot_start.time() < timezone.localtime().time():
                 is_available = False

            if is_available:
                slots.append(slot_start.strftime('%H:%M'))

            current_time += datetime.timedelta(minutes=30) # Intervalo de 30 min

        return JsonResponse({'slots': slots})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# --- VISTAS EXISTENTES (Igual que antes) ---

@login_required
def create_employee_view(request):
    try:
        salon = request.user.salon
    except:
        messages.error(request, "Solo los dueños pueden ver esto.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            # ... (Lógica de creación de empleado igual a la versión anterior)
            pass 
    else:
        form = EmployeeCreationForm()
    return render(request, 'dashboard/create_employee.html', {'form': form, 'salon': salon})

@login_required
def salon_settings_view(request):
    salon = get_object_or_404(Salon, owner=request.user)
    HoursFormSet = modelformset_factory(OpeningHours, form=OpeningHoursForm, extra=0)
    # ... (Resto de lógica igual)
    return render(request, 'dashboard/settings.html', {'salon_form': SalonCreateForm(instance=salon), 'hours_formset': HoursFormSet(queryset=salon.opening_hours.all()), 'salon': salon})

@login_required
def employee_settings_view(request):
    # ... (Resto de lógica igual)
    return render(request, 'dashboard/employee_dashboard.html', {}) # Simplificado para brevedad, usa tu código original aquí

@login_required
def services_settings_view(request):
    # ... (Resto de lógica igual)
    return render(request, 'dashboard/services.html', {})

def salon_detail(request, slug):
    salon = get_object_or_404(Salon, slug=slug)
    services = salon.services.all()
    
    # Estado Abierto/Cerrado
    now = timezone.localtime(timezone.now())
    today_hours = salon.opening_hours.filter(weekday=now.weekday()).first()
    is_open = False
    if today_hours and not today_hours.is_closed:
        if today_hours.from_hour <= now.time() <= today_hours.to_hour:
            is_open = True

    selected_service = None
    service_id = request.POST.get('service') or request.GET.get('service')
    if service_id:
        selected_service = Service.objects.filter(id=service_id).first()

    if request.method == 'POST':
        form = BookingForm(request.POST, service=selected_service)
        if form.is_valid():
            try:
                booking = create_booking_service(salon, selected_service, request.user, form.cleaned_data)
                notify_new_booking(booking)
                messages.success(request, f"¡Reserva confirmada con {booking.employee.name} a las {booking.start_time.strftime('%H:%M')}!")
                return redirect('salon_detail', slug=slug)
            except Exception as e:
                messages.error(request, f"Error: {e}")
    else:
        form = BookingForm(service=selected_service)

    return render(request, 'salon_detail.html', {
        'salon': salon,
        'form': form,
        'selected_service': selected_service,
        'services': services,
        'is_open': is_open
    })