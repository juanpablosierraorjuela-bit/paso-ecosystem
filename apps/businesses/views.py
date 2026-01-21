from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, time, datetime, date
import calendar
import re
from django.db.models import Q

from apps.core.models import GlobalSettings, User
from apps.marketplace.models import Appointment
from .models import Service, Salon, EmployeeWeeklySchedule
from .forms import (
    ServiceForm, EmployeeCreationForm, SalonScheduleForm, 
    OwnerUpdateForm, SalonUpdateForm
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

# --- PANEL DE EMPLEADO (SOLO SEMANAL) ---

@login_required
def employee_dashboard(request):
    if request.user.role not in ['EMPLOYEE', 'OWNER']: 
        return redirect('dashboard')
    
    hoy = timezone.localtime(timezone.now())
    
    # 1. Obtener parámetros de fecha con limpieza
    raw_month = str(request.GET.get('month', hoy.month))
    raw_year = str(request.GET.get('year', hoy.year))
    clean_month = re.sub(r'\D', '', raw_month)
    clean_year = re.sub(r'\D', '', raw_year)
    
    mes_seleccionado = int(clean_month) if clean_month else hoy.month
    anio_seleccionado = int(clean_year) if clean_year else hoy.year

    # 2. Lógica para generar las semanas CORRECTAS del mes seleccionado
    # Usamos date objects para calcular los lunes reales y evitar errores de etiqueta
    weeks_info = []
    processed_iso_weeks = []
    
    # Obtener el primer y último día del mes
    last_day = calendar.monthrange(anio_seleccionado, mes_seleccionado)[1]
    
    for day in range(1, last_day + 1):
        current_date = date(anio_seleccionado, mes_seleccionado, day)
        iso_year, iso_week, iso_weekday = current_date.isocalendar()
        
        # Identificador único de semana (Año ISO + Semana ISO)
        week_key = (iso_year, iso_week)
        
        if week_key not in processed_iso_weeks:
            processed_iso_weeks.append(week_key)
            
            # Calcular Lunes y Domingo reales de esta semana ISO
            # Lunes = FechaActual - (DiaSemanaISO - 1)
            monday_of_week = current_date - timedelta(days=iso_weekday - 1)
            sunday_of_week = monday_of_week + timedelta(days=6)
            
            # Formato de etiqueta bonito: "10 Jun - 16 Jun"
            label = f"{monday_of_week.day} {calendar.month_name[monday_of_week.month][:3]} - {sunday_of_week.day} {calendar.month_name[sunday_of_week.month][:3]}"
            
            # Buscar o Crear (SIN ACTIVAR) el horario
            # IMPORTANTE: active_days='' por defecto para que aparezca "Cerrado" hasta que el usuario lo active
            week_schedule, created = EmployeeWeeklySchedule.objects.get_or_create(
                employee=request.user,
                year=iso_year, 
                week_number=iso_week,
                defaults={
                    'work_start': time(9,0),
                    'work_end': time(18,0),
                    'active_days': '' # VACÍO POR DEFECTO: El empleado debe entrar y guardar para activar
                }
            )
            
            weeks_info.append({
                'label': label,
                'instance': week_schedule,
                'range': label # Usamos la misma etiqueta corregida
            })

    # 3. Citas del empleado
    appointments = Appointment.objects.filter(
        employee=request.user,
        date_time__date__gte=hoy.date()
    ).exclude(status='CANCELLED').order_by('date_time')

    # 4. Formularios de Perfil
    profile_form = OwnerUpdateForm(instance=request.user)
    password_form = SetPasswordForm(user=request.user)

    if request.method == 'POST':
        # ACTUALIZAR SEMANA
        if 'update_week' in request.POST:
            week_id = request.POST.get('week_id')
            # Recuperamos por ID, que ya existe gracias al get_or_create del GET
            week_inst = get_object_or_404(EmployeeWeeklySchedule, id=week_id, employee=request.user)
            
            try:
                # Actualizar horas
                week_inst.work_start = request.POST.get('work_start')
                week_inst.work_end = request.POST.get('work_end')
                
                # Actualizar días activos
                # Si el usuario no marca nada, days será [] y active_days será "", por lo tanto NO DISPONIBLE
                days = request.POST.getlist('days') 
                week_inst.active_days = ",".join(days)
                
                week_inst.save()
                messages.success(request, f"Horario actualizado correctamente.")
            except Exception:
                messages.error(request, "Error al guardar los horarios.")
            
            return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")

        # ACTUALIZAR PERFIL
        elif 'update_profile' in request.POST:
            profile_form = OwnerUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Perfil actualizado.")
                return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")

        # CAMBIAR CONTRASEÑA
        elif 'change_password' in request.POST:
            password_form = SetPasswordForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña actualizada.")
                return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'salon': request.user.workplace if request.user.role == 'EMPLOYEE' else getattr(request.user, 'owned_salon', None),
        'appointments': appointments,
        'weeks_info': weeks_info,
        'months_range': [(i, calendar.month_name[i].capitalize()) for i in range(1, 13)],
        'years_range': [hoy.year, hoy.year + 1],
        'mes_seleccionado': mes_seleccionado,
        'anio_seleccionado': anio_seleccionado,
    }
    return render(request, 'businesses/employee_dashboard.html', context)