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

    # Verifica si cada salón está abierto ahora para mostrarlo en el front
    for salon in salons:
        salon.is_open_now = AvailabilityManager.is_salon_open(salon)

    cities = Salon.objects.values_list('city', flat=True).distinct().order_by('city')

    return render(request, 'index.html', {
        'salons': salons,
        'cities': cities,
        'current_query': query,
        'current_city': city
    })

def salon_detail(request, pk):
    """Detalle del salón y lista de servicios."""
    salon = get_object_or_404(Salon, pk=pk)
    services = salon.services.all()
    
    # Lógica de apertura
    is_open = AvailabilityManager.is_salon_open(salon)

    return render(request, 'salon_detail.html', {
        'salon': salon,
        'services': services,
        'is_open': is_open
    })

@login_required
def booking_wizard(request, salon_id):
    """Proceso de reserva de cita."""
    salon = get_object_or_404(Salon, id=salon_id)
    service_ids = request.GET.getlist('service')
    services = Service.objects.filter(id__in=service_ids, salon=salon)
    
    if not services:
        messages.error(request, "Debes seleccionar al menos un servicio.")
        return redirect('salon_detail', pk=salon_id)

    employees = User.objects.filter(workplace=salon, role='EMPLOYEE')
    
    context = {
        'salon': salon,
        'services': services,
        'employees': employees,
        'total_price': sum(s.price for s in services),
    }
    return render(request, 'marketplace/booking_wizard.html', context)

def get_available_slots_api(request):
    """API para cargar slots disponibles vía AJAX."""
    employee_id = request.GET.get('employee_id')
    date_str = request.GET.get('date')
    service_ids = request.GET.getlist('services[]')

    if not all([employee_id, date_str, service_ids]):
        return JsonResponse({'slots': []})

    employee = get_object_or_404(User, id=employee_id)
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    services = Service.objects.filter(id__in=service_ids)
    
    slots = AvailabilityManager.get_available_slots(employee.workplace, services, employee, target_date)
    return JsonResponse({'slots': slots})

@login_required
def booking_commit(request):
    """Finaliza la creación de la cita."""
    if request.method == 'POST':
        salon_id = request.POST.get('salon_id')
        employee_id = request.POST.get('employee_id')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        service_ids = request.POST.getlist('services')

        salon = get_object_or_404(Salon, id=salon_id)
        employee = get_object_or_404(User, id=employee_id)
        services = Service.objects.filter(id__in=service_ids)
        
        total_price = sum(s.price for s in services)
        deposit = (total_price * salon.deposit_percentage) / 100

        dt_str = f"{date_str} {time_str}"
        booking_dt = timezone.make_aware(datetime.strptime(dt_str, '%Y-%m-%d %H:%M'))

        appointment = Appointment.objects.create(
            client=request.user,
            salon=salon,
            employee=employee,
            date_time=booking_dt,
            total_price=total_price,
            deposit_amount=deposit,
            status='PENDING'
        )
        appointment.services.set(services)
        
        messages.success(request, "Cita reservada. Pendiente de pago de abono.")
        return redirect('client_dashboard')
    return redirect('home')

# --- VISTAS DE GESTIÓN (DASHBOARD DUEÑO) ---

@login_required
def owner_dashboard(request):
    if request.user.role != 'OWNER':
        if request.user.role == 'EMPLOYEE':
            return redirect('employee_dashboard')
        return redirect('marketplace_home')
    
    try:
        salon = request.user.owned_salon
    except:
        return redirect('register_owner')

    # Validación de timestamp nulo
    reg_ts = request.user.registration_timestamp or timezone.now()
    elapsed_time = timezone.now() - reg_ts
    time_limit = timedelta(hours=24)
    remaining_time = time_limit - elapsed_time
    total_seconds_left = max(0, int(remaining_time.total_seconds()))

    admin_settings = GlobalSettings.objects.first()
    raw_phone = admin_settings.whatsapp_support if (admin_settings and admin_settings.whatsapp_support) else '573000000000'
    clean_phone = re.sub(r'\D', '', str(raw_phone))
    if not clean_phone.startswith('57'): clean_phone = '57' + clean_phone
        
    wa_message = f"Hola, soy el dueño de {salon.name} (ID {request.user.id}). Adjunto comprobante de renovación."
    wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_message)}"

    # Citas del negocio
    appointments = Appointment.objects.filter(salon=salon).order_by('-date_time')
    for app in appointments:
        app.balance_due = app.total_price - app.deposit_amount

    employees = User.objects.filter(workplace=salon, role='EMPLOYEE')

    context = {
        'salon': salon,
        'appointments': appointments,
        'seconds_left': total_seconds_left,
        'wa_link': wa_link,
        'is_trial': not request.user.is_verified_payment,
        'service_count': salon.services.count(),
        'employee_count': employees.count(),
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
    if request.user.role != 'OWNER': return redirect('marketplace_home')
    salon = request.user.owned_salon
    services = salon.services.all()

    from .forms import ServiceForm
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
    if request.user.role != 'OWNER': return redirect('marketplace_home')
    salon = request.user.owned_salon
    service = get_object_or_404(Service, pk=pk, salon=salon)
    
    from .forms import ServiceForm
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
    if request.user.role != 'OWNER': return redirect('marketplace_home')
    service = get_object_or_404(Service, pk=pk, salon=request.user.owned_salon)
    service.delete()
    messages.success(request, "Servicio eliminado.")
    return redirect('services_list')

@login_required
def employees_list(request):
    if request.user.role != 'OWNER': return redirect('marketplace_home')
    salon = request.user.owned_salon
    employees = User.objects.filter(workplace=salon, role='EMPLOYEE')
    
    from .forms import EmployeeCreationForm
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
    if request.user.role != 'OWNER': return redirect('marketplace_home')
    employee = get_object_or_404(User, pk=pk, workplace=request.user.owned_salon)
    employee.delete()
    messages.success(request, "Empleado eliminado.")
    return redirect('employees_list')

@login_required
def settings_view(request):
    if request.user.role != 'OWNER': return redirect('marketplace_home')
    salon = request.user.owned_salon
    
    from .forms import OwnerUpdateForm, SalonUpdateForm, SalonScheduleForm
    
    owner_form = OwnerUpdateForm(instance=request.user)
    salon_form = SalonUpdateForm(instance=salon)
    schedule_form = SalonScheduleForm(instance=salon)
    # NUEVO: Instancia del formulario de contraseña para el Dueño
    password_form = SetPasswordForm(user=request.user)

    if request.method == 'POST':
        # 1. ACTUALIZAR PERFIL E IDENTIDAD
        if 'update_profile' in request.POST:
            owner_form = OwnerUpdateForm(request.POST, instance=request.user)
            salon_form = SalonUpdateForm(request.POST, instance=salon)
            if owner_form.is_valid() and salon_form.is_valid():
                owner_form.save()
                salon_form.save()
                messages.success(request, "Identidad y datos de negocio guardados.")
                return redirect('settings_view')

        # 2. ACTUALIZAR REGLAS Y HORARIOS
        elif 'update_schedule' in request.POST:
            schedule_form = SalonScheduleForm(request.POST, instance=salon)
            if schedule_form.is_valid():
                instancia_horario = schedule_form.save(commit=False)
                dias_seleccionados = request.POST.getlist('active_days')
                instancia_horario.active_days = ",".join(dias_seleccionados)
                instancia_horario.save()
                messages.success(request, "Horarios y reglas de abono actualizados.")
                return redirect('settings_view')
            else:
                messages.error(request, "Error al validar los horarios. Revisa el formato.")

        # 3. NUEVO: ACTUALIZAR CONTRASEÑA (DUEÑO)
        elif 'update_password' in request.POST:
            password_form = SetPasswordForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Tu contraseña ha sido actualizada con éxito.")
                return redirect('settings_view')
            else:
                messages.error(request, "Error al actualizar la contraseña. Revisa los requisitos.")

    return render(request, 'businesses/settings.html', {
        'owner_form': owner_form, 
        'salon_form': salon_form,
        'schedule_form': schedule_form,
        'password_form': password_form, # Se pasa al context
        'salon': salon
    })

# --- PANEL DE EMPLEADO ---

@login_required
def employee_dashboard(request):
    if request.user.role not in ['EMPLOYEE', 'OWNER']: 
        return redirect('dashboard')
    
    hoy = timezone.localtime(timezone.now())
    raw_month = str(request.GET.get('month', hoy.month))
    raw_year = str(request.GET.get('year', hoy.year))
    clean_month = re.sub(r'\D', '', raw_month)
    clean_year = re.sub(r'\D', '', raw_year)
    
    mes_seleccionado = int(clean_month) if clean_month else hoy.month
    anio_seleccionado = int(clean_year) if clean_year else hoy.year

    cal = calendar.Calendar(firstweekday=0) 
    month_days = cal.monthdayscalendar(anio_seleccionado, mes_seleccionado)
    
    weeks_info = []
    processed_weeks = []

    for week in month_days:
        for day in week:
            if day != 0:
                dt = datetime(anio_seleccionado, mes_seleccionado, day)
                iso_year, iso_week, _ = dt.isocalendar()
                
                if iso_week not in processed_weeks:
                    processed_weeks.append(iso_week)
                    week_schedule, _ = EmployeeWeeklySchedule.objects.get_or_create(
                        employee=request.user,
                        year=iso_year, 
                        week_number=iso_week,
                        defaults={
                            'work_start': time(9,0),
                            'work_end': time(18,0),
                            'active_days': '0,1,2,3,4,5'
                        }
                    )
                    start_of_week = dt - timedelta(days=dt.weekday())
                    end_of_week = start_of_week + timedelta(days=6)
                    
                    weeks_info.append({
                        'number': iso_week,
                        'instance': week_schedule,
                        'range': f"{start_of_week.strftime('%d %b')} - {end_of_week.strftime('%d %b')}"
                    })
                break
    
    appointments = Appointment.objects.filter(
        employee=request.user,
        date_time__date__gte=hoy.date()
    ).exclude(status='CANCELLED').order_by('date_time')

    from .forms import OwnerUpdateForm
    profile_form = OwnerUpdateForm(instance=request.user)
    password_form = SetPasswordForm(user=request.user)

    if request.method == 'POST':
        if 'update_week' in request.POST:
            week_id = request.POST.get('week_id')
            week_inst = get_object_or_404(EmployeeWeeklySchedule, id=week_id, employee=request.user)
            week_inst.work_start = request.POST.get('work_start')
            week_inst.work_end = request.POST.get('work_end')
            days = request.POST.getlist('days') 
            week_inst.active_days = ",".join(days)
            week_inst.save()
            messages.success(request, "Horario semanal actualizado.")
            return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")

        elif 'update_profile' in request.POST:
            profile_form = OwnerUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Perfil actualizado.")
                return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")
        
        # NUEVO: Procesar cambio de contraseña en Dashboard de Empleado
        elif 'update_password' in request.POST:
            password_form = SetPasswordForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña actualizada.")
                return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")
            else:
                messages.error(request, "Error al cambiar la contraseña.")

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
    """Dashboard para el cliente final."""
    appointments = Appointment.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'marketplace/client_dashboard.html', {'appointments': appointments})