from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, time, datetime
import calendar
from apps.core.models import GlobalSettings, User
from apps.marketplace.models import Appointment
from .models import Service, Salon, EmployeeSchedule, EmployeeWeeklySchedule
from .forms import ServiceForm, EmployeeCreationForm, SalonScheduleForm, OwnerUpdateForm, SalonUpdateForm, EmployeeScheduleUpdateForm
import re
from django.db.models import Q

# --- VISTAS PÚBLICAS (MARKETPLACE) ---

def marketplace_home(request):
    query = request.GET.get('q', '')
    city = request.GET.get('city', '')
    
    # Empezamos con todos los salones
    salons = Salon.objects.all()

    if query:
        # Busca en el nombre del salón O en los nombres de sus servicios
        salons = salons.filter(
            Q(name__icontains=query) | 
            Q(services__name__icontains=query)
        ).distinct() 

    if city:
        salons = salons.filter(city=city)

    cities = Salon.objects.values_list('city', flat=True).distinct()

    return render(request, 'marketplace/home.html', {
        'salons': salons,
        'cities': cities,
        'query': query,
        'selected_city': city
    })

def salon_detail(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    services = salon.services.all()
    employees = User.objects.filter(workplace=salon, role='EMPLOYEE')
    
    return render(request, 'marketplace/salon_detail.html', {
        'salon': salon,
        'services': services,
        'employees': employees
    })

# --- DASHBOARD DEL DUEÑO ---

@login_required
def owner_dashboard(request):
    if request.user.role != 'OWNER':
        return redirect('marketplace_home')
        
    salon = getattr(request.user, 'owned_salon', None)
    if not salon:
        return render(request, 'businesses/no_salon.html')

    # Citas del día para este salón
    today = timezone.localtime(timezone.now()).date()
    appointments = Appointment.objects.filter(
        services__salon=salon,
        date_time__date=today
    ).distinct().order_by('date_time')

    return render(request, 'businesses/owner_dashboard.html', {
        'salon': salon,
        'appointments': appointments,
        'today': today
    })

@login_required
def services_list(request):
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
        
    return render(request, 'businesses/services_list.html', {
        'services': services,
        'form': form
    })

@login_required
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk, salon=request.user.owned_salon)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio actualizado.")
            return redirect('services_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'businesses/service_form.html', {'form': form, 'service': service})

@login_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk, salon=request.user.owned_salon)
    service.delete()
    messages.success(request, "Servicio eliminado.")
    return redirect('services_list')

@login_required
def employees_list(request):
    salon = request.user.owned_salon
    employees = User.objects.filter(workplace=salon, role='EMPLOYEE')
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                role='EMPLOYEE',
                workplace=salon,
                phone=form.cleaned_data.get('phone', '')
            )
            # Crear horario base por defecto
            EmployeeSchedule.objects.create(employee=user)
            messages.success(request, f"Empleado {user.first_name} creado.")
            return redirect('employees_list')
    else:
        form = EmployeeCreationForm()
        
    return render(request, 'businesses/employees_list.html', {
        'employees': employees,
        'form': form
    })

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(User, pk=pk, workplace=request.user.owned_salon, role='EMPLOYEE')
    employee.delete()
    messages.success(request, "Empleado eliminado.")
    return redirect('employees_list')

@login_required
def settings_view(request):
    salon = request.user.owned_salon
    if request.method == 'POST':
        form = SalonUpdateForm(request.POST, instance=salon)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración actualizada.")
            return redirect('settings_view')
    else:
        form = SalonUpdateForm(instance=salon)
    return render(request, 'businesses/settings.html', {'form': form, 'salon': salon})

@login_required
def verify_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Seguridad: Solo el dueño del salón o el empleado asignado pueden verificar
    if request.user.role == 'OWNER' or request.user == appointment.employee:
        appointment.is_verified = True
        appointment.save()
        messages.success(request, "Cita verificada correctamente.")
    
    return redirect(request.META.get('HTTP_REFERER', 'marketplace_home'))

# --- DASHBOARD DEL EMPLEADO (MI AGENDA) ---

@login_required
def employee_dashboard(request):
    if request.user.role != 'EMPLOYEE':
        return redirect('marketplace_home')

    hoy = timezone.localtime(timezone.now())
    
    # --- CORRECCIÓN ERROR 500 (Procesamiento robusto de parámetros) ---
    try:
        raw_month = str(request.GET.get('month', request.POST.get('month', hoy.month)))
        raw_year = str(request.GET.get('year', request.POST.get('year', hoy.year)))
        
        # Limpiamos puntos y comas (ej: "2.026" -> "2026")
        mes_seleccionado = int(raw_month.split('.')[0])
        anio_seleccionado = int(raw_year.replace('.', '').replace(',', ''))
    except (ValueError, TypeError, AttributeError):
        mes_seleccionado = hoy.month
        anio_seleccionado = hoy.year

    # Horario Base
    schedule, created = EmployeeSchedule.objects.get_or_create(employee=request.user)
    
    # Formularios
    schedule_form = EmployeeScheduleUpdateForm(instance=schedule)
    from apps.core.forms import UserProfileForm
    profile_form = UserProfileForm(instance=request.user)
    password_form = SetPasswordForm(user=request.user)

    if request.method == 'POST':
        # Guardar Horario Base
        if 'update_schedule' in request.POST:
            schedule_form = EmployeeScheduleUpdateForm(request.POST, instance=schedule)
            if schedule_form.is_valid():
                schedule_form.save()
                messages.success(request, "Horario base actualizado.")
                return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")
        
        # Guardar Configuración Semanal Específica
        elif 'update_weekly' in request.POST:
            iso_year = int(request.POST.get('year_val'))
            iso_week = int(request.POST.get('week_val'))
            
            week_inst, _ = EmployeeWeeklySchedule.objects.get_or_create(
                employee=request.user, 
                year=iso_year, 
                week_number=iso_week
            )
            
            week_inst.work_start = request.POST.get('work_start')
            week_inst.work_end = request.POST.get('work_end')
            week_inst.lunch_start = request.POST.get('lunch_start')
            week_inst.lunch_end = request.POST.get('lunch_end')
            week_inst.is_active = request.POST.get('is_active') == 'on'
            week_inst.save()
            
            messages.success(request, f"Semana {iso_week} actualizada.")
            return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")

        # Guardar Perfil
        elif 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Perfil actualizado.")
                return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")

        # Cambiar Contraseña
        elif 'change_password' in request.POST:
            password_form = SetPasswordForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña actualizada.")
                return redirect(f"{request.path}?month={mes_seleccionado}&year={anio_seleccionado}")
            else:
                messages.error(request, "Error al cambiar la contraseña.")

    # Lógica de Calendario
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(anio_seleccionado, mes_seleccionado)
    
    weeks_data = []
    for week in month_days:
        first_day = week[0]
        iso_year, iso_week, _ = first_day.isocalendar()
        
        # Buscar si hay horario específico para esta semana
        specific_week = EmployeeWeeklySchedule.objects.filter(
            employee=request.user, 
            year=iso_year, 
            week_number=iso_week
        ).first()
        
        weeks_data.append({
            'iso_week': iso_week,
            'iso_year': iso_year,
            'start': first_day,
            'end': week[-1],
            'instance': specific_week if specific_week else schedule
        })

    # Citas Verificadas
    verified_appointments = Appointment.objects.filter(
        employee=request.user,
        is_verified=True
    ).order_by('-date_time')[:10]

    months_range = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]
    years_range = [hoy.year, hoy.year + 1]
    
    salon_context = request.user.workplace if request.user.role == 'EMPLOYEE' else getattr(request.user, 'owned_salon', None)

    return render(request, 'businesses/employee_dashboard.html', {
        'schedule_form': schedule_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'schedule': schedule,
        'weeks_data': weeks_data,
        'verified_appointments': verified_appointments,
        'mes_sel': mes_seleccionado,
        'anio_sel': anio_seleccionado,
        'months_range': months_range,
        'years_range': years_range,
        'salon': salon_context
    })