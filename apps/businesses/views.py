from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta, time, datetime
import calendar
import re
import urllib.parse
import uuid
from decimal import Decimal
from django.db.models import Q

# Importes de tus modelos y lógica
from apps.core.models import GlobalSettings, User
from apps.marketplace.models import Appointment
from apps.businesses.models import Service, Salon, EmployeeWeeklySchedule, EmployeeSchedule
from apps.businesses.logic import AvailabilityManager
from apps.businesses.forms import (
    SalonUpdateForm, OwnerUpdateForm, EmployeeScheduleUpdateForm, 
    ServiceForm, EmployeeCreationForm, SalonScheduleForm
)

# LISTA DE MESES EN ESPAÑOL PARA EL DASHBOARD
MESES_ESP = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

# --- VISTAS PÚBLICAS (MARKETPLACE) ---

def marketplace_home(request):
    """Vista principal del marketplace con buscador y filtros."""
    query = request.GET.get('q', '')
    city = request.GET.get('city', '')
    
    salons = Salon.objects.all()

    if query:
        salons = salons.filter(
            Q(name__icontains=query) | 
            Q(services__name__icontains=query)
        ).distinct()

    if city:
        salons = salons.filter(city=city)

    now = timezone.localtime(timezone.now())
    current_time = now.time()
    
    # Marcamos qué salones están abiertos "ya mismo" visualmente
    for salon in salons:
        is_open_today = False
        if salon.active_days and str(now.weekday()) in salon.active_days.split(','):
            if salon.opening_time and salon.closing_time:
                if salon.opening_time <= current_time <= salon.closing_time:
                    is_open_today = True
        salon.is_open_now = is_open_today

    return render(request, 'marketplace/home.html', {
        'salons': salons,
        'query': query,
        'selected_city': city,
        'cities': Salon.objects.values_list('city', flat=True).distinct()
    })

def salon_detail(request, pk):
    """Vista pública del perfil del salón."""
    salon = get_object_or_404(Salon, pk=pk)
    services = salon.services.all()
    employees = User.objects.filter(workplace=salon, role='EMPLOYEE')
    
    today_idx = timezone.localtime(timezone.now()).weekday()
    
    # Procesamos horarios de empleados para mostrar hoy
    for emp in employees:
        schedule = EmployeeSchedule.objects.filter(employee=emp).first()
        emp.today_hours = None
        if schedule and schedule.active_days:
            if str(today_idx) in schedule.active_days.split(','):
                emp.today_hours = f"{schedule.work_start.strftime('%I:%M %p')} - {schedule.work_end.strftime('%I:%M %p')}"
            else:
                emp.today_hours = "No trabaja hoy"
        else:
            emp.today_hours = "Sin horario"

    return render(request, 'marketplace/salon_detail.html', {
        'salon': salon,
        'services': services,
        'employees': employees
    })

def booking_view(request, salon_id):
    """Paso 1: Seleccionar Servicios."""
    salon = get_object_or_404(Salon, pk=salon_id)
    if request.method == 'POST':
        service_ids = request.POST.getlist('services')
        if not service_ids:
            messages.error(request, "Selecciona al menos un servicio.")
            return redirect('booking_view', salon_id=salon.id)
        
        # Guardamos selección en sesión
        request.session['booking_salon_id'] = salon.id
        request.session['booking_service_ids'] = service_ids
        return redirect('booking_schedule', salon_id=salon.id)
        
    services = salon.services.all()
    return render(request, 'marketplace/booking_services.html', {'salon': salon, 'services': services})

def booking_schedule(request, salon_id):
    """Paso 2: Seleccionar Fecha, Hora y Empleado."""
    salon = get_object_or_404(Salon, pk=salon_id)
    service_ids = request.session.get('booking_service_ids', [])
    if not service_ids:
        return redirect('booking_view', salon_id=salon.id)
        
    services = Service.objects.filter(id__in=service_ids)
    total_duration = sum(s.duration_minutes for s in services)
    employees = User.objects.filter(workplace=salon, role='EMPLOYEE')
    
    today = timezone.localtime(timezone.now()).date()
    
    context = {
        'salon': salon,
        'services': services,
        'total_duration': total_duration,
        'employees': employees,
        'today': today.strftime("%Y-%m-%d"),
    }
    return render(request, 'marketplace/booking_schedule.html', context)

def get_available_slots(request):
    """API JSON para devolver horarios disponibles."""
    salon_id = request.GET.get('salon_id')
    employee_id = request.GET.get('employee_id')
    date_str = request.GET.get('date')
    duration = int(request.GET.get('duration', 30))
    
    if not all([salon_id, date_str]):
        return JsonResponse({'error': 'Faltan datos'}, status=400)
        
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'error': 'Fecha inválida'}, status=400)
        
    salon = get_object_or_404(Salon, pk=salon_id)
    
    # Si se selecciona empleado, filtramos por él. Si no, probamos con todos.
    if employee_id:
        employees = [get_object_or_404(User, pk=employee_id)]
    else:
        employees = User.objects.filter(workplace=salon, role='EMPLOYEE')
        
    all_slots = []
    seen_times = set()
    
    for emp in employees:
        slots = AvailabilityManager.get_available_slots(salon, emp, target_date, duration)
        for slot in slots:
            # Si "cualquier empleado", unimos horarios sin repetir
            if slot['time'] not in seen_times:
                all_slots.append(slot)
                seen_times.add(slot['time'])
                
    # Ordenar por hora
    all_slots.sort(key=lambda x: x['time'])
    
    return JsonResponse({'slots': all_slots})

@login_required
def booking_commit(request):
    """Paso 3: Confirmar y Pagar Abono."""
    if request.method == 'POST':
        salon_id = request.POST.get('salon_id')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        employee_id = request.POST.get('employee_id')
        
        salon = get_object_or_404(Salon, pk=salon_id)
        client = request.user
        
        # Parse fecha/hora
        appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        appt_time = datetime.strptime(time_str, "%H:%M").time()
        start_dt = datetime.combine(appt_date, appt_time)
        
        # Recuperar servicios
        service_ids = request.session.get('booking_service_ids', [])
        services = Service.objects.filter(id__in=service_ids)
        total_price = sum(s.price for s in services)
        duration = sum(s.duration_minutes for s in services)
        
        # Calcular abono
        deposit_amount = 0
        if salon.deposit_percentage > 0:
            deposit_amount = (total_price * salon.deposit_percentage) / 100
            
        balance_due = total_price - deposit_amount
        
        end_dt = start_dt + timedelta(minutes=duration)
        
        # Crear Cita
        appt = Appointment.objects.create(
            client=client,
            salon=salon,
            employee_id=employee_id if employee_id else None,
            start_time=timezone.make_aware(start_dt),
            end_time=timezone.make_aware(end_dt),
            total_price=total_price,
            deposit_amount=deposit_amount,
            balance_due=balance_due,
            status='CONFIRMED' # O PENDING si integras pasarela real
        )
        appt.services.set(services)
        
        # Limpiar sesión
        if 'booking_salon_id' in request.session: del request.session['booking_salon_id']
        if 'booking_service_ids' in request.session: del request.session['booking_service_ids']
        
        messages.success(request, f"¡Cita confirmada! Abono registrado: ${deposit_amount:,.0f}")
        return redirect('client_dashboard')
        
    return redirect('marketplace_home')


# --- VISTAS PRIVADAS (DUEÑOS Y EMPLEADOS) ---

@login_required
def dashboard_view(request):
    """Redirige al dashboard correcto según el rol."""
    if request.user.role == 'OWNER':
        return owner_dashboard(request)
    elif request.user.role == 'EMPLOYEE':
        return employee_dashboard(request)
    else:
        return redirect('client_dashboard')

@login_required
def settings_view(request):
    """Vista unificada de configuración para Dueños."""
    if request.user.role != 'OWNER':
        return redirect('dashboard')

    salon = request.user.owned_salon
    
    # Formularios
    owner_form = OwnerUpdateForm(instance=request.user)
    salon_form = SalonUpdateForm(instance=salon)
    schedule_form = SalonScheduleForm(instance=salon)

    if request.method == 'POST':
        if 'update_owner' in request.POST:
            owner_form = OwnerUpdateForm(request.POST, instance=request.user)
            if owner_form.is_valid():
                owner_form.save()
                messages.success(request, "Perfil actualizado.")
                return redirect('settings_view')

        elif 'update_salon' in request.POST:
            salon_form = SalonUpdateForm(request.POST, instance=salon)
            if salon_form.is_valid():
                salon_form.save()
                messages.success(request, "Datos del negocio actualizados.")
                return redirect('settings_view')
                
        elif 'update_schedule' in request.POST:
            schedule_form = SalonScheduleForm(request.POST, instance=salon)
            if schedule_form.is_valid():
                schedule_form.save()
                messages.success(request, "Reglas de operación actualizadas (Horario y Abonos).")
                # IMPORTANTE: Forzamos recarga para que logic.py lea los nuevos active_days
                return redirect('settings_view')

    context = {
        'owner_form': owner_form,
        'salon_form': salon_form,
        'schedule_form': schedule_form,
    }
    return render(request, 'businesses/settings.html', context)

@login_required
def owner_dashboard(request):
    """Panel principal del dueño."""
    salon = request.user.owned_salon
    if not salon:
        return redirect('setup_salon')

    # Filtros de fecha
    hoy = timezone.localtime(timezone.now())
    mes_seleccionado = int(request.GET.get('month', hoy.month))
    anio_seleccionado = int(request.GET.get('year', hoy.year))
    
    # Citas del mes
    appointments = Appointment.objects.filter(
        salon=salon,
        start_time__year=anio_seleccionado,
        start_time__month=mes_seleccionado
    ).order_by('start_time')

    # Formularios rápidos
    service_form = ServiceForm()
    employee_form = EmployeeCreationForm()

    # Procesamiento de formularios (Servicios y Empleados)
    if request.method == 'POST':
        if 'create_service' in request.POST:
            sf = ServiceForm(request.POST)
            if sf.is_valid():
                s = sf.save(commit=False)
                s.salon = salon
                s.save()
                messages.success(request, "Servicio agregado.")
                return redirect('dashboard')
        
        elif 'create_employee' in request.POST:
            ef = EmployeeCreationForm(request.POST)
            if ef.is_valid():
                user = ef.save(commit=False)
                user.set_password(ef.cleaned_data['password'])
                user.role = 'EMPLOYEE'
                user.workplace = salon
                user.save()
                messages.success(request, "Empleado creado.")
                return redirect('dashboard')

    context = {
        'salon': salon,
        'appointments': appointments,
        'services': salon.services.all(),
        'employees': User.objects.filter(workplace=salon, role='EMPLOYEE'),
        'service_form': service_form,
        'employee_form': employee_form,
        # CORRECCIÓN: Usamos MESES_ESP en lugar de calendar
        'months_range': [(i, MESES_ESP[i]) for i in range(1, 13)],
        'years_range': [hoy.year, hoy.year + 1],
        'mes_seleccionado': mes_seleccionado,
        'anio_seleccionado': anio_seleccionado,
    }
    return render(request, 'businesses/dashboard.html', context)

@login_required
def employee_dashboard(request):
    """Panel para empleados."""
    if request.user.role != 'EMPLOYEE':
        return redirect('dashboard')

    # Cambio de contraseña y perfil
    profile_form = OwnerUpdateForm(instance=request.user)
    password_form = SetPasswordForm(request.user)

    # Filtros de fecha
    hoy = timezone.localtime(timezone.now())
    mes_seleccionado = int(request.GET.get('month', hoy.month))
    anio_seleccionado = int(request.GET.get('year', hoy.year))

    appointments = Appointment.objects.filter(
        employee=request.user,
        start_time__year=anio_seleccionado,
        start_time__month=mes_seleccionado
    ).order_by('start_time')
    
    # Manejo de horarios semanales
    weeks_info = []
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(anio_seleccionado, mes_seleccionado)
    
    for week in month_days:
        week_label = f"Semana {week[0].strftime('%d')} - {week[-1].strftime('%d %b')}"
        # Aquí simplificamos la lógica de visualización
        weeks_info.append({'label': week_label, 'days': week})

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = OwnerUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Perfil actualizado.")
                return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")
        
        elif 'change_password' in request.POST:
            password_form = SetPasswordForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, "Contraseña actualizada.")
                return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")

        elif 'update_schedule' in request.POST:
            # Lógica para guardar horario (simplificada para este ejemplo)
            # Normalmente aquí procesarías EmployeeScheduleUpdateForm
            pass

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'salon': request.user.workplace,
        'appointments': appointments,
        'weeks_info': weeks_info,
        # CORRECCIÓN: Usamos MESES_ESP
        'months_range': [(i, MESES_ESP[i]) for i in range(1, 13)],
        'years_range': [hoy.year, hoy.year + 1],
        'mes_seleccionado': mes_seleccionado,
        'anio_seleccionado': anio_seleccionado,
    }
    return render(request, 'businesses/employee_dashboard.html', context)

@login_required
def cancel_appointment(request, pk):
    """Lógica para cancelar citas."""
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.user == appointment.client or request.user.role == 'OWNER':
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.success(request, "Cita cancelada.")
        return redirect('dashboard' if request.user.role == 'OWNER' else 'client_dashboard')
    return redirect('marketplace_home')

@login_required
def client_dashboard(request):
    """Panel del cliente."""
    appointments = Appointment.objects.filter(client=request.user).order_by('-start_time')
    return render(request, 'marketplace/client_dashboard.html', {'appointments': appointments})