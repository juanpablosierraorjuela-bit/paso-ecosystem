from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.contrib import messages
from django.utils import timezone

from .models import Salon, OpeningHours, Employee, Booking, EmployeeSchedule
from .forms import SalonCreateForm, OpeningHoursForm, BookingForm, EmployeeSettingsForm, EmployeeScheduleForm
from .utils import send_telegram_message

@login_required
def salon_settings_view(request):
    salon = get_object_or_404(Salon, owner=request.user)
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
            messages.success(request, "Configuración guardada.")
            return redirect('dashboard')
    else:
        salon_form = SalonCreateForm(instance=salon)
        hours_formset = HoursFormSet(queryset=salon.opening_hours.all())
    return render(request, 'dashboard/settings.html', {'salon_form': salon_form, 'hours_formset': hours_formset, 'salon': salon})

@login_required
def employee_settings_view(request):
    """
    PANEL DEL EMPLEADO: Aquí configura sus horarios.
    """
    # Intentamos obtener el perfil de empleado del usuario logueado
    try:
        employee = request.user.employee
    except Exception:
        # Si no tiene perfil, lo mandamos a la pantalla de unirse
        return redirect('employee_join')
    
    # Crear horarios por defecto si es la primera vez que entra
    if employee.schedules.count() < 7:
        for i in range(7):
            EmployeeSchedule.objects.get_or_create(
                employee=employee, weekday=i, 
                defaults={'from_hour': '09:00', 'to_hour': '18:00', 'is_closed': False}
            )

    # Formset para editar los 7 días
    ScheduleFormSet = modelformset_factory(EmployeeSchedule, form=EmployeeScheduleForm, extra=0)

    if request.method == 'POST':
        settings_form = EmployeeSettingsForm(request.POST, instance=employee)
        schedule_formset = ScheduleFormSet(request.POST, queryset=employee.schedules.all())

        if settings_form.is_valid() and schedule_formset.is_valid():
            settings_form.save()
            schedule_formset.save()
            messages.success(request, "¡Horario actualizado correctamente!")
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
    
    if request.method == 'POST':
        form = BookingForm(request.POST, service=None)
        service = None
        
        # Recuperar servicio seleccionado
        if 'service' in request.POST:
            from .models import Service
            try:
                service = Service.objects.get(id=request.POST.get('service'))
                form = BookingForm(request.POST, service=service)
            except:
                pass

        if form.is_valid() and service:
            booking = form.save(commit=False)
            booking.salon = salon
            booking.service = service
            if request.user.is_authenticated:
                booking.customer = request.user
            
            booking.end_time = booking.start_time + timezone.timedelta(minutes=service.duration_minutes)
            
            # --- VALIDACIÓN DE HORARIO DEL EMPLEADO ---
            if booking.employee:
                try:
                    weekday = booking.start_time.weekday()
                    schedule = booking.employee.schedules.get(weekday=weekday)
                    emp_time = booking.start_time.time()
                    
                    # Si el empleado cerró ese día o la hora no cuadra
                    if schedule.is_closed or not (schedule.from_hour <= emp_time <= schedule.to_hour):
                        messages.error(request, f"Lo sentimos, {booking.employee.name} no trabaja en ese horario.")
                        return render(request, 'salon_detail.html', {'salon': salon, 'form': form})
                except:
                    pass # Si falla la validación por algo técnico, permitimos reservar

            booking.save()

            # Notificaciones Telegram
            msg = f"🔔 *Nueva Reserva*\n\n📅 {booking.start_time.strftime('%d/%m %H:%M')}\n👤 {booking.customer_name}\n💇 {service.name}"
            if salon.telegram_bot_token and salon.telegram_chat_id:
                send_telegram_message(salon.telegram_bot_token, salon.telegram_chat_id, msg)
            if booking.employee and booking.employee.telegram_bot_token and booking.employee.telegram_chat_id:
                send_telegram_message(booking.employee.telegram_bot_token, booking.employee.telegram_chat_id, msg)

            messages.success(request, "¡Reserva confirmada!")
            return redirect('salon_detail', slug=slug)
    else:
        form = BookingForm()

    return render(request, 'salon_detail.html', {'salon': salon, 'form': form})