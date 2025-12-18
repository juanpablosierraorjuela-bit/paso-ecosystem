import json
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Salon, OpeningHours, EmployeeSchedule, Employee, Service, Booking
from .forms import (
    SalonCreateForm, OpeningHoursForm, BookingForm, 
    EmployeeSettingsForm, EmployeeScheduleForm, EmployeeCreationForm,
    ServiceForm
)
from .services import create_booking_service, get_day_slots
from .utils import notify_new_booking

User = get_user_model()

# --- API DE DISPONIBILIDAD ---
def get_available_slots_api(request, salon_slug):
    if request.method != 'GET': return JsonResponse({'error': 'Método no permitido'}, status=405)
    date_str = request.GET.get('date')
    employee_id = request.GET.get('employee')
    service_id = request.GET.get('service')
    if not date_str or not employee_id: return JsonResponse({'slots': []})
    salon = get_object_or_404(Salon, slug=salon_slug)
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        employee = Employee.objects.get(id=employee_id, salon=salon)
        service = Service.objects.get(id=service_id) if service_id else None
        duration = service.duration_minutes if service else 30
        slots = get_day_slots(salon, employee, target_date, duration)
        return JsonResponse({'slots': slots})
    except Exception as e: return JsonResponse({'error': str(e)}, status=400)

# --- VISTA PÚBLICA / VITRINA ---
def salon_detail(request, slug):
    salon = get_object_or_404(Salon, slug=slug)
    service_id = request.POST.get('service') or request.GET.get('service')
    service = None
    if service_id:
        try: service = Service.objects.get(id=service_id, salon=salon)
        except: pass

    if request.method == 'POST':
        data = request.POST.copy()
        if data.get('date_picked') and data.get('time_picked'):
            data['start_time'] = f"{data.get('date_picked')} {data.get('time_picked')}"
        
        form = BookingForm(data, service=service)
        if form.is_valid():
            try:
                booking = create_booking_service(salon, service, request.user, form.cleaned_data)
                notify_new_booking(booking)
                messages.success(request, f"¡Reserva confirmada! Te esperamos el {booking.start_time.strftime('%d/%m a las %H:%M')}")
                return redirect('salon_detail', slug=slug)
            except ValueError as e: messages.error(request, str(e))
            except Exception: messages.error(request, "Error inesperado.")
        else: messages.error(request, "Verifica los datos.")
    else: form = BookingForm(service=service)

    return render(request, 'salon_detail.html', {'salon': salon, 'form': form, 'selected_service': service})

# --- GESTIÓN DE SERVICIOS ---
@login_required
def manage_services_view(request):
    try: salon = request.user.salon
    except: return redirect('dashboard')
    services = salon.services.all()
    return render(request, 'dashboard/services.html', {'salon': salon, 'services': services})

@login_required
def add_service_view(request):
    try: salon = request.user.salon
    except: return redirect('dashboard')
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            s = form.save(commit=False)
            s.salon = salon
            s.save()
            messages.success(request, "Servicio creado.")
            return redirect('manage_services')
    else: form = ServiceForm()
    return render(request, 'dashboard/service_form.html', {'form': form, 'title': 'Crear Servicio'})

@login_required
def edit_service_view(request, service_id):
    try: salon = request.user.salon; service = get_object_or_404(Service, id=service_id, salon=salon)
    except: return redirect('dashboard')
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid(): form.save(); messages.success(request, "Actualizado."); return redirect('manage_services')
    else: form = ServiceForm(instance=service)
    return render(request, 'dashboard/service_form.html', {'form': form, 'title': 'Editar Servicio'})

@login_required
def delete_service_view(request, service_id):
    try: salon = request.user.salon; get_object_or_404(Service, id=service_id, salon=salon).delete(); messages.success(request, "Eliminado.")
    except: pass
    return redirect('manage_services')

# --- EMPLEADOS Y AJUSTES (AQUÍ ESTABA EL ERROR, ESTO FALTABA) ---
@login_required
def create_employee_view(request):
    try: salon = request.user.salon
    except: return redirect('dashboard')
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            if User.objects.filter(email=d['email']).exists(): messages.error(request, "Email ya registrado.")
            else:
                with transaction.atomic():
                    u = User.objects.create_user(username=d['email'], email=d['email'], password=d['password'], role='EMPLOYEE')
                    Employee.objects.create(salon=salon, user=u, name=d['name'], phone=d['phone'])
                messages.success(request, "Empleado creado.")
                return redirect('dashboard')
    else: form = EmployeeCreationForm()
    return render(request, 'dashboard/create_employee.html', {'form': form, 'salon': salon})

@login_required
def salon_settings_view(request):
    salon = get_object_or_404(Salon, owner=request.user)
    if salon.opening_hours.count() < 7:
        for i in range(7): OpeningHours.objects.get_or_create(salon=salon, weekday=i, defaults={'from_hour': '09:00', 'to_hour': '18:00'})
    HoursFormSet = modelformset_factory(OpeningHours, form=OpeningHoursForm, extra=0)
    if request.method == 'POST':
        f = SalonCreateForm(request.POST, request.FILES, instance=salon)
        h = HoursFormSet(request.POST, queryset=salon.opening_hours.all())
        if f.is_valid() and h.is_valid(): f.save(); h.save(); messages.success(request, "Guardado."); return redirect('dashboard')
    else: f = SalonCreateForm(instance=salon); h = HoursFormSet(queryset=salon.opening_hours.all())
    return render(request, 'dashboard/settings.html', {'salon_form': f, 'hours_formset': h, 'salon': salon})

@login_required
def employee_settings_view(request):
    try: emp = request.user.employee
    except: return redirect('home')
    if emp.schedules.count() < 7:
        for i in range(7): EmployeeSchedule.objects.get_or_create(employee=emp, weekday=i, defaults={'from_hour':'09:00','to_hour':'18:00'})
    ScheduleFormSet = modelformset_factory(EmployeeSchedule, form=EmployeeScheduleForm, extra=0)
    if request.method == 'POST':
        f = EmployeeSettingsForm(request.POST, instance=emp)
        s = ScheduleFormSet(request.POST, queryset=emp.schedules.all())
        if f.is_valid() and s.is_valid(): f.save(); s.save(); messages.success(request, "Guardado."); return redirect('dashboard')
    else: f = EmployeeSettingsForm(instance=emp); s = ScheduleFormSet(queryset=emp.schedules.all())
    return render(request, 'dashboard/employee_dashboard.html', {'settings_form': f, 'schedule_formset': s, 'employee': emp})