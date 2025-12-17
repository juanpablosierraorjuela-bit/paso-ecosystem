from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.contrib import messages
from django.utils import timezone

from .models import Salon, OpeningHours, EmployeeSchedule
from .forms import SalonCreateForm, OpeningHoursForm, BookingForm, EmployeeSettingsForm, EmployeeScheduleForm
# Importamos nuestros nuevos servicios
from .services import create_booking_service
from .utils import notify_new_booking

@login_required
def salon_settings_view(request):
    salon = get_object_or_404(Salon, owner=request.user)
    # Crear horarios default si no existen
    if salon.opening_hours.count() < 7:
        for i in range(7):
            OpeningHours.objects.get_or_create(salon=salon, weekday=i, defaults={'from_hour': '09:00', 'to_hour': '18:00'})
            
    HoursFormSet = modelformset_factory(OpeningHours, form=OpeningHoursForm, extra=0)
    
    if request.method == 'POST':
        salon_form = SalonCreateForm(request.POST, request.FILES, instance=salon)
        hours_formset = HoursFormSet(request.POST, queryset=salon.opening_hours.all())
        
        if salon_form.is_valid() and hours_formset.is_valid():
            salon_form.save()
            hours_formset.save()
            messages.success(request, "Configuración de negocio guardada exitosamente.")
            return redirect('dashboard')
    else:
        salon_form = SalonCreateForm(instance=salon)
        hours_formset = HoursFormSet(queryset=salon.opening_hours.all())
        
    return render(request, 'dashboard/settings.html', {
        'salon_form': salon_form, 
        'hours_formset': hours_formset, 
        'salon': salon
    })

@login_required
def employee_settings_view(request):
    try:
        employee = request.user.employee
    except:
        messages.warning(request, "No tienes perfil de empleado asociado.")
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
            messages.success(request, "Perfil profesional actualizado.")
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
    """
    Vista pública de reserva NIVEL DIOS.
    Maneja validaciones complejas y notificaciones.
    """
    salon = get_object_or_404(Salon, slug=slug)
    
    # Obtener el servicio seleccionado (si viene por POST o GET)
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
                messages.error(request, "Por favor selecciona un servicio válido.")
            else:
                try:
                    # --- AQUÍ LA MAGIA ---
                    # Delegamos la complejidad al servicio
                    booking = create_booking_service(
                        salon=salon,
                        service=service,
                        customer=request.user,
                        form_data=form.cleaned_data
                    )
                    
                    # Notificar
                    notify_new_booking(booking)
                    
                    messages.success(request, f"¡Reserva confirmada con {booking.employee.name}!")
                    # Limpiamos el formulario tras el éxito
                    return redirect('salon_detail', slug=slug)
                    
                except ValueError as e:
                    # Capturamos errores de validación lógica (ej. "Ya está ocupado")
                    messages.error(request, str(e))
                except Exception as e:
                    # Errores inesperados
                    messages.error(request, f"Ocurrió un error inesperado: {str(e)}")
    else:
        form = BookingForm(service=service)

    return render(request, 'salon_detail.html', {
        'salon': salon, 
        'form': form,
        'selected_service': service
    })