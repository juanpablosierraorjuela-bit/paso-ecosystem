from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, time, datetime
import calendar
import re
from django.db.models import Q

from apps.core.models import GlobalSettings, User
from apps.marketplace.models import Appointment
from .models import Service, Salon, EmployeeSchedule, EmployeeWeeklySchedule
from .forms import (
    ServiceForm, EmployeeCreationForm, SalonScheduleForm, 
    OwnerUpdateForm, SalonUpdateForm, EmployeeScheduleUpdateForm
)

# --- VISTAS PÚBLICAS (MARKETPLACE) ---

def marketplace_home(request):
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

    cities = Salon.objects.values_list('city', flat=True).distinct()

    return render(request, 'index.html', {
        'salons': salons,
        'cities': cities,
        'current_query': query,
        'current_city': city
    })

def salon_detail(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    services = salon.services.all()
    
    now = timezone.localtime(timezone.now()).time()
    is_open = False
    if salon.opening_time and salon.closing_time:
        is_open = salon.opening_time <= now <= salon.closing_time

    return render(request, 'salon_detail.html', {
        'salon': salon,
        'services': services,
        'is_open': is_open
    })

# --- VISTAS DE GESTIÓN (DASHBOARD DUEÑO) ---

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
        
    wa_message = f"Hola, soy el dueño de {salon.name} (ID {request.user.id}). Adjunto mi comprobante de pago para renovar mi membresía."
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
    try:
        salon = request.user.owned_salon
        appointment = get_object_or_404(Appointment, id=appointment_id, salon=salon)
        appointment.status = 'VERIFIED'
        appointment.save()
        messages.success(request, f"Cita de {appointment.client.first_name} verificada.")
    except Exception:
        messages.error(request, "No se pudo verificar la cita.")
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
            messages.success(request, "Servicio actualizado.")
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
                user_obj = owner_form.save(commit=False)
                new_pw = owner_form.cleaned_data.get('new_password')
                if new_pw:
                    user_obj.set_password(new_pw)
                user_obj.save()
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

# --- PANEL DE EMPLEADO (CALENDARIO Y CITAS) ---

@login_required
def employee_dashboard(request):
    if request.user.role not in ['EMPLOYEE', 'OWNER']: 
        return redirect('dashboard')
    
    hoy = timezone.localtime(timezone.now())
    mes_seleccionado = int(request.GET.get('month', request.POST.get('month', hoy.month)))
    anio_seleccionado = int(request.GET.get('year', request.POST.get('year', hoy.year)))

    cal = calendar.Calendar(firstweekday=0) 
    month_days = cal.monthdayscalendar(anio_seleccionado, mes_seleccionado)
    
    weeks_info = []
    processed_weeks = []

    # 1. Obtener horario base para usarlo como default
    schedule, _ = EmployeeSchedule.objects.get_or_create(
        employee=request.user, 
        defaults={'work_start': time(9,0), 'work_end': time(18,0)}
    )

    for week in month_days:
        for day in week:
            if day != 0:
                dt = datetime(anio_seleccionado, mes_seleccionado, day)
                iso_year, iso_week, _ = dt.isocalendar()
                
                if iso_week not in processed_weeks:
                    processed_weeks.append(iso_week)
                    # Al crear una semana, usamos las horas del horario base por defecto
                    week_schedule, _ = EmployeeWeeklySchedule.objects.get_or_create(
                        employee=request.user,
                        year=iso_year, 
                        week_number=iso_week,
                        defaults={
                            'work_start': schedule.work_start,
                            'work_end': schedule.work_end,
                            'active_days': schedule.active_days
                        }
                    )
                    start_of_week = dt - timedelta(days=dt.weekday())
                    end_of_week = start_of_week + timedelta(days=6)
                    
                    weeks_info.append({
                        'number': iso_week,
                        'instance': week_schedule,
                        'label': f"Semana {iso_week}",
                        'range': f"{start_of_week.strftime('%d %b')} - {end_of_week.strftime('%d %b')}"
                    })
                break
    
    appointments = Appointment.objects.filter(
        employee=request.user,
        status='VERIFIED'
    ).order_by('date_time')
    
    for app in appointments:
        app.balance_due = app.total_price - app.deposit_amount

    schedule_form = EmployeeScheduleUpdateForm(instance=schedule)
    profile_form = OwnerUpdateForm(instance=request.user)
    password_form = SetPasswordForm(user=request.user)

    if request.method == 'POST':
        if 'update_schedule' in request.POST:
            schedule_form = EmployeeScheduleUpdateForm(request.POST, instance=schedule)
            if schedule_form.is_valid():
                schedule_form.save()
                messages.success(request, "Horario base actualizado.")
                return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")
        
        elif 'update_week' in request.POST:
            week_id = request.POST.get('week_id')
            week_inst = get_object_or_404(EmployeeWeeklySchedule, id=week_id, employee=request.user)
            try:
                # CORRECCIÓN: Ahora sí tomamos los valores del formulario
                new_start = request.POST.get('work_start')
                new_end = request.POST.get('work_end')
                
                if new_start: week_inst.work_start = new_start
                if new_end: week_inst.work_end = new_end
                
                days = request.POST.getlist('days') 
                week_inst.active_days = ",".join(days)
                week_inst.save()
                messages.success(request, f"Semana {week_inst.week_number} guardada correctamente.")
            except Exception:
                messages.error(request, "Error al guardar los horarios de la semana.")
            return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")

        elif 'update_profile' in request.POST:
            profile_form = OwnerUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Perfil actualizado.")
                return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")

        elif 'change_password' in request.POST:
            password_form = SetPasswordForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña actualizada.")
                return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")
            else:
                messages.error(request, "Error al actualizar la contraseña. Revisa los requisitos.")

    months_range = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]
    years_range = [hoy.year, hoy.year + 1]
    
    if request.user.role == 'EMPLOYEE':
        salon_context = request.user.workplace
    else:
        salon_context = getattr(request.user, 'owned_salon', None)

    return render(request, 'businesses/employee_dashboard.html', {
        'schedule_form': schedule_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'schedule': schedule,
        'salon': salon_context,
        'appointments': appointments,
        'weeks_info': weeks_info,
        'months_range': months_range,
        'years_range': years_range,
        'mes_sel': mes_seleccionado,
        'anio_sel': anio_seleccionado,
    })