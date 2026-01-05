from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment
from apps.businesses.models import Service
from django.utils import timezone
from datetime import timedelta

@login_required
def create_appointment(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        # Crear Cita PENDIENTE
        start_time = timezone.now().replace(second=0, microsecond=0) + timedelta(hours=1)
        end_time = start_time + timedelta(minutes=service.duration_minutes)
        abono = (service.price * service.business.deposit_percentage) / 100
        
        Appointment.objects.create(
            business=service.business,
            client=request.user,
            employee=service.business.staff.first(), # MVP: Primer empleado disponible
            service=service,
            date=start_time.date(),
            start_time=start_time.time(),
            end_time=end_time.time(),
            status='PENDING', # Clave: Nace pendiente
            deposit_amount=abono,
            total_price=service.price
        )
        messages.success(request, "¡Reserva creada! Tienes 60 min para abonar.")
        return redirect('booking:client_dashboard')
    return redirect('marketplace:home')

@login_required
def verify_payment(request, appointment_id):
    # Solo el dueño verifica
    cita = get_object_or_404(Appointment, id=appointment_id)
    if request.user == cita.business.owner:
        cita.status = 'VERIFIED'
        cita.save()
        messages.success(request, "Cita confirmada exitosamente.")
        return redirect('businesses:dashboard')
    return redirect('home')

@login_required
def client_dashboard(request):
    appointments = Appointment.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'booking/client_dashboard.html', {'appointments': appointments})

@login_required
def employee_dashboard(request):
    appointments = Appointment.objects.filter(employee=request.user, status='VERIFIED').order_by('date', 'start_time')
    return render(request, 'booking/employee_dashboard.html', {'appointments': appointments})

@login_required
def employee_schedule(request): return render(request, 'booking/schedule.html') # Placeholder validado
@login_required
def employee_profile(request): return render(request, 'booking/profile.html') # Placeholder validado
