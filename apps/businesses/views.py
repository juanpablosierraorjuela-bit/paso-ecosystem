from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

# Modelos
from .models import Salon, OpeningHours, EmployeeSchedule, Employee
# Forms
# CORRECCIÓN: Importamos SalonForm en lugar de SalonCreateForm
from .forms import SalonForm, OpeningHoursForm, BookingForm, EmployeeSettingsForm, EmployeeScheduleForm, EmployeeCreationForm
# Servicios
from .services import create_booking_service
from .utils import notify_new_booking

User = get_user_model()

@login_required
def create_employee_view(request):
    """
    VISTA NUEVA: El dueño registra manualmente a su empleado.
    """
    try:
        salon = request.user.salon
    except:
        messages.error(request, "Solo los dueños de salón pueden registrar empleados.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data['email']
            password = data['password']
            name = data['name']
            phone = data['phone']

            # Verificamos si el usuario ya existe
            if User.objects.filter(email=email).exists():
                messages.error(request, f"El correo {email} ya está registrado en la plataforma.")
            else:
                try:
                    with transaction.atomic():
                        # 1. Crear Usuario
                        user = User.objects.create_user(
                            username=email, # Usamos email como username
                            email=email,
                            password=password,
                            role='EMPLOYEE'
                        )
                        
                        # 2. Crear Perfil Empleado y Vincular
                        Employee.objects.create(
                            salon=salon,
                            user=user,
                            name=name,
                            phone=phone
                        )
                    
                    messages.success(request, f"¡Empleado {name} creado! Ahora puede entrar con su correo y contraseña.")
                    return redirect('dashboard')
                    
                except Exception as e:
                    messages.error(request, f"Error creando empleado: {e}")
    else:
        form = EmployeeCreationForm()

    return render(request, 'dashboard/create_employee.html', {'form': form, 'salon': salon})

@login_required
def salon_settings_view(request):
    salon = get_object_or_404(Salon, owner=request.user)
    if salon.opening_hours.count() < 7:
        for i in range(7):
            OpeningHours.objects.get_or_create(salon=salon, weekday=i, defaults={'from_hour': '09:00', 'to_hour': '18:00'})
            
    HoursFormSet = modelformset_factory(OpeningHours, form=OpeningHoursForm, extra=0)
    
    if request.method == 'POST':
        # CORRECCIÓN: Usamos SalonForm aquí
        salon_form = SalonForm(request.POST, request.FILES, instance=salon)
        hours_formset = HoursFormSet(request.POST, queryset=salon.opening_hours.all())
        
        if salon_form.is_valid() and hours_formset.is_valid():
            salon_form.save()
            hours_formset.save()
            messages.success(request, "Configuración guardada.")
            return redirect('dashboard')
    else:
        # CORRECCIÓN: Y aquí también
        salon_form = SalonForm(instance=salon)
        hours_formset = HoursFormSet(queryset=salon.opening_hours.all())
        
    return render(request, 'dashboard/settings.html', {'salon_form': salon_form, 'hours_formset': hours_formset, 'salon': salon})

@login_required
def employee_settings_view(request):
    try:
        employee = request.user.employee
    except:
        messages.warning(request, "No tienes perfil de empleado.")
        return redirect('home')
    
    if employee.schedules.count() < 7:
        for i in range(7):
            EmployeeSchedule.objects.get_or_create(
                employee=employee, weekday=i, 
                defaults={'from_hour': '09:00', 'to_hour': '18:00', 'is_closed': False}
            )

    ScheduleFormSet = modelformset_factory(EmployeeSchedule, form=EmployeeScheduleForm, extra=0)

    if request.method == 'POST':
        settings_form = EmployeeSettingsForm(request.POST, instance=employee)
        schedule_formset = ScheduleFormSet(request.POST, queryset=employee.schedules.all())

        if settings_form.is_valid() and schedule_formset.is_valid():
            settings_form.save()
            schedule_formset.save()
            messages.success(request, "Perfil actualizado.")
            return redirect('dashboard')
    else:
        settings_form = EmployeeSettingsForm(instance=employee)
        schedule_formset = ScheduleFormSet(queryset=employee.schedules.all())

    return render(request, 'dashboard/employee_dashboard.html', {
        'settings_form': settings_form,
        'schedule_formset': schedule_formset,
        'employee': employee
    })

def salon_detail(request, slug):
    salon = get_object_or_404(Salon, slug=slug)
    service_id = request.POST.get('service') or request.GET.get('service')
    service = None
    if service_id:
        from .models import Service
        try:
            service = Service.objects.get(id=service_id, salon=salon)
        except Service.DoesNotExist:
            service = None

    if request.method == 'POST':
        form = BookingForm(request.POST, service=service)
        if form.is_valid():
            if not service:
                messages.error(request, "Selecciona un servicio.")
            else:
                try:
                    booking = create_booking_service(salon, service, request.user, form.cleaned_data)
                    notify_new_booking(booking)
                    messages.success(request, f"¡Reserva confirmada con {booking.employee.name}!")
                    return redirect('salon_detail', slug=slug)
                except ValueError as e:
                    messages.error(request, str(e))
                except Exception as e:
                    messages.error(request, "Error inesperado.")
    else:
        form = BookingForm(service=service)

    return render(request, 'salon_detail.html', {'salon': salon, 'form': form, 'selected_service': service})