from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, time, datetime
import calendar
import urllib.parse

from apps.core.models import User
from apps.marketplace.models import Appointment
from .models import Service, Salon, EmployeeSchedule, EmployeeWeeklySchedule
from .forms import (
    ServiceForm, EmployeeCreationForm, SalonScheduleForm, 
    OwnerUpdateForm, SalonUpdateForm, EmployeeScheduleUpdateForm
)
from django.db.models import Q

# --- VISTAS DE GESTIÓN DE SALÓN (OWNER) ---

@login_required
def owner_dashboard(request):
    if request.user.role != 'OWNER':
        return redirect('home')
    
    salon = get_object_or_404(Salon, owner=request.user)
    # Citas del salón que requieren atención o confirmadas
    appointments = Appointment.objects.filter(salon=salon).order_by('-date_time')
    
    return render(request, 'businesses/owner_dashboard.html', {
        'salon': salon,
        'appointments': appointments
    })

@login_required
def services_list(request):
    salon = get_object_or_404(Salon, owner=request.user)
    services = Service.objects.filter(salon=salon)
    
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.salon = salon
            service.save()
            messages.success(request, "Servicio añadido correctamente.")
            return redirect('services_list')
    else:
        form = ServiceForm()
        
    return render(request, 'businesses/services_list.html', {
        'services': services,
        'form': form
    })

# --- VISTA PRINCIPAL DEL EMPLEADO (DASHBOARD) ---

@login_required
def employee_dashboard(request):
    # Determinar si es empleado o dueño viendo su propia agenda
    is_employee = request.user.role == 'EMPLOYEE'
    salon = request.user.workplace if is_employee else getattr(request.user, 'owned_salon', None)
    
    if not salon:
        messages.error(request, "No tienes un salón asociado.")
        return redirect('home')

    hoy = timezone.localtime(timezone.now())
    
    # 1. Gestión de Fecha (Mes y Año)
    try:
        mes_seleccionado = int(request.GET.get('month', hoy.month))
        anio_seleccionado = int(request.GET.get('year', hoy.year))
    except ValueError:
        mes_seleccionado, anio_seleccionado = hoy.month, hoy.year

    # 2. Obtener o crear Horario Base
    schedule, created = EmployeeSchedule.objects.get_or_create(employee=request.user)

    # 3. Lógica de Calendario (Semanas del mes)
    cal = calendar.Calendar(firstweekday=0) # Lunes = 0
    month_days = cal.monthdatescalendar(anio_seleccionado, mes_seleccionado)
    
    weeks_info = []
    for week in month_days:
        # Usamos el jueves de la semana para determinar el número de semana ISO
        # Esto evita problemas con semanas que saltan de año
        reference_day = week[3] 
        year_iso, week_num, _ = reference_day.isocalendar()
        
        instancia_semana, _ = EmployeeWeeklySchedule.objects.get_or_create(
            employee=request.user,
            year=year_iso,
            week_number=week_num,
            defaults={
                'work_start': schedule.work_start,
                'work_end': schedule.work_end,
                'active_days': schedule.active_days
            }
        )
        
        weeks_info.append({
            'label': f"Semana {week_num}",
            'range': f"{week[0].strftime('%d %b')} - {week[-1].strftime('%d %b')}",
            'instance': instancia_semana
        })

    # 4. Procesamiento de Formularios (POST)
    schedule_form = EmployeeScheduleUpdateForm(instance=schedule)
    profile_form = OwnerUpdateForm(instance=request.user) # Reutiliza campos de nombre/tel
    password_form = SetPasswordForm(user=request.user)

    if request.method == 'POST':
        # Actualizar Semana Específica
        if 'update_week' in request.POST:
            week_id = request.POST.get('week_id')
            week_inst = get_object_or_404(EmployeeWeeklySchedule, id=week_id, employee=request.user)
            week_inst.work_start = request.POST.get('work_start')
            week_inst.work_end = request.POST.get('work_end')
            # Checkboxes de días
            days_list = request.POST.getlist('days')
            week_inst.active_days = ",".join(days_list)
            week_inst.save()
            messages.success(request, f"Horario de la {week_inst.week_number} actualizado.")
            
        # Actualizar Horario Base
        elif 'update_schedule' in request.POST:
            schedule_form = EmployeeScheduleUpdateForm(request.POST, instance=schedule)
            if schedule_form.is_valid():
                schedule_form.save()
                messages.success(request, "Horario base actualizado.")
        
        # Actualizar Perfil
        elif 'update_profile' in request.POST:
            profile_form = OwnerUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Perfil actualizado.")
        
        # Cambiar Contraseña
        elif 'change_password' in request.POST:
            password_form = SetPasswordForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña actualizada.")
            else:
                messages.error(request, "Error en el formulario de contraseña.")

        return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")

    # 5. Citas del empleado
    appointments = Appointment.objects.filter(
        employee=request.user,
        status='CONFIRMED'
    ).select_related('client').prefetch_related('services').order_by('date_time')

    # Datos para los selectores del template
    months_range = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]
    
    return render(request, 'businesses/employee_dashboard.html', {
        'weeks_info': weeks_info,
        'appointments': appointments,
        'schedule_form': schedule_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'mes_sel': mes_seleccionado,
        'anio_sel': anio_seleccionado,
        'months_range': months_range,
        'years_range': [hoy.year, hoy.year + 1],
        'salon': salon
    })

# --- VERIFICACIÓN DE CITAS (PARA EL DUEÑO) ---

@login_required
def verify_appointment(request, appointment_id):
    """ El dueño marca como CONFIRMED tras recibir el pago/comprobante """
    if request.user.role != 'OWNER':
        messages.error(request, "Acceso denegado.")
        return redirect('home')
        
    appointment = get_object_or_404(Appointment, id=appointment_id, salon__owner=request.user)
    
    if appointment.status == 'PENDING':
        appointment.status = 'CONFIRMED'
        appointment.save()
        messages.success(request, f"Cita de {appointment.client.first_name} verificada con éxito.")
    else:
        messages.info(request, "La cita ya no está pendiente.")
        
    return redirect('dashboard')

# --- OTRAS FUNCIONES AUXILIARES (EJEMPLO CANCELACIÓN) ---

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Solo el cliente dueño de la cita o el dueño del salón pueden cancelar
    if appointment.client == request.user or appointment.salon.owner == request.user:
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.success(request, "Cita cancelada.")
    else:
        messages.error(request, "No tienes permiso.")
        
    return redirect('dashboard' if request.user.role == 'OWNER' else 'client_dashboard')