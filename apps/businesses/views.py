from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import datetime
import uuid

from .forms import (
    SalonForm, OpeningHoursForm, BookingForm, 
    EmployeeSettingsForm, EmployeeScheduleForm, ServiceForm
)
from .models import Salon, Service, Booking, Employee, OpeningHours, EmployeeSchedule

@login_required
def dashboard(request):
    # Validar que sea ADMIN
    if getattr(request.user, 'role', '') != 'ADMIN':
        return redirect('home')

    # Obtener Salón
    try:
        salon = request.user.salon
    except:
        # Si no tiene salón, crearlo
        if request.method == 'POST':
            form = SalonForm(request.POST, request.FILES)
            if form.is_valid():
                salon = form.save(commit=False)
                salon.owner = request.user
                salon.save()
                # Horarios Default
                for i in range(6): OpeningHours.objects.create(salon=salon, weekday=i, from_hour=datetime.time(8,0), to_hour=datetime.time(20,0))
                OpeningHours.objects.create(salon=salon, weekday=6, from_hour=datetime.time(9,0), to_hour=datetime.time(15,0), is_closed=True)
                return redirect('dashboard')
        else:
            form = SalonForm()
        return render(request, 'dashboard/create_salon.html', {'form': form})

    # Formularios vacíos
    form = SalonForm(instance=salon)
    s_form = ServiceForm()
    h_form = OpeningHoursForm()
    
    # PROCESAR FORMULARIOS
    if request.method == 'POST':
        # 1. Actualizar Datos del Negocio
        if 'update_settings' in request.POST:
            form = SalonForm(request.POST, request.FILES, instance=salon)
            if form.is_valid():
                form.save()
                messages.success(request, 'Negocio actualizado.')
                return redirect('dashboard')
        
        # 2. CREAR SERVICIO (Esta es la parte nueva que pediste)
        elif 'create_service' in request.POST:
            s_form = ServiceForm(request.POST)
            if s_form.is_valid():
                srv = s_form.save(commit=False)
                srv.salon = salon
                srv.save()
                messages.success(request, 'Servicio agregado exitosamente.')
                return redirect('dashboard')
        
        # 3. Actualizar Horario
        elif 'update_hours' in request.POST:
            h_form = OpeningHoursForm(request.POST)
            if h_form.is_valid():
                OpeningHours.objects.update_or_create(
                    salon=salon, weekday=h_form.cleaned_data['weekday'],
                    defaults={
                        'from_hour': h_form.cleaned_data['from_hour'], 
                        'to_hour': h_form.cleaned_data['to_hour'], 
                        'is_closed': h_form.cleaned_data['is_closed']
                    }
                )
                messages.success(request, 'Horario actualizado.')
                return redirect('dashboard')

    # Generar Token de invitación si falta
    if not salon.invite_token:
        salon.invite_token = uuid.uuid4()
        salon.save()

    invite_link = f"http://{request.get_host()}/unete/{salon.invite_token}/"

    return render(request, 'dashboard/index.html', {
        'salon': salon,
        'form': form,
        's_form': s_form,
        'h_form': h_form,
        'services': salon.services.all(),  # Lista de servicios para mostrar
        'employees': salon.employees.all(),
        'bookings': salon.bookings.all().order_by('-start_time'),
        'hours': salon.opening_hours.all().order_by('weekday'),
        'invite_link': invite_link
    })

# Vistas auxiliares para compatibilidad
def create_salon_view(request): return dashboard(request)
def manage_services_view(request): return dashboard(request)
def manage_employees_view(request): return dashboard(request)
def manage_schedule_view(request): return dashboard(request)
def settings_view(request): return dashboard(request)