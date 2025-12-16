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
    """Configuración del Salón (Solo Dueños)"""
    salon = get_object_or_404(Salon, owner=request.user)
    
    # Asegurar que existan los 7 días de horario
    if salon.opening_hours.count() < 7:
        for i in range(7):
            OpeningHours.objects.get_or_create(
                salon=salon, 
                weekday=i, 
                defaults={'from_hour': '09:00', 'to_hour': '18:00', 'is_closed': False}
            )

    # Formset para editar los 7 días a la vez
    HoursFormSet = modelformset_factory(OpeningHours, form=OpeningHoursForm, extra=0)
    
    if request.method == 'POST':
        salon_form = SalonCreateForm(request.POST, request.FILES, instance=salon)
        hours_formset = HoursFormSet(request.POST, queryset=salon.opening_hours.all())
        
        if salon_form.is_valid() and hours_formset.is_valid():
            salon_form.save()
            hours_formset.save()
            messages.success(request, "Configuración guardada correctamente.")
            return redirect('dashboard')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
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
    """Configuración del Empleado"""
    employee = get_object_or_404(Employee, user=request.user)
    
    if employee.schedules.count() < 7:
        for i in range(7):
            EmployeeSchedule.objects.get_or_create(
                employee=employee, 
                weekday=i, 
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
    
    if request.method == 'POST':
        form = BookingForm(request.POST, service=None)
        if 'service' in request.POST:
            from .models import Service
            service_id = request.POST.get('service')
            try:
                service = Service.objects.get(id=service_id)
                form = BookingForm(request.POST, service=service)
            except Service.DoesNotExist:
                service = None

        if form.is_valid() and service:
            booking = form.save(commit=False)
            booking.salon = salon
            booking.service = service
            if request.user.is_authenticated:
                booking.customer = request.user
            
            booking.end_time = booking.start_time + timezone.timedelta(minutes=service.duration_minutes)
            booking.save()

            # Notificaciones Telegram
            msg = f"🔔 *Nueva Reserva*\n\n📅 {booking.start_time.strftime('%Y-%m-%d %H:%M')}\n👤 {booking.customer_name}\n💇 {service.name}\n📞 {booking.customer_phone}"
            
            if salon.telegram_bot_token and salon.telegram_chat_id:
                send_telegram_message(salon.telegram_bot_token, salon.telegram_chat_id, msg)

            if booking.employee and booking.employee.telegram_bot_token and booking.employee.telegram_chat_id:
                msg_emp = f"🔔 *Tienes una nueva cita*\n\n📅 {booking.start_time}\n👤 {booking.customer_name}\n💇 {service.name}"
                send_telegram_message(booking.employee.telegram_bot_token, booking.employee.telegram_chat_id, msg_emp)

            messages.success(request, "¡Reserva confirmada!")
            return redirect('salon_detail', slug=slug)
    else:
        form = BookingForm()

    return render(request, 'salon_detail.html', {'salon': salon, 'form': form})