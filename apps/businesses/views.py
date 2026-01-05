from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.booking.models import Appointment
from django.utils import timezone

@login_required
def owner_dashboard(request):
    try:
        business = request.user.business_profile
        
        # --- LÓGICA DEL PORTERO (24H REAPER) ---
        hours_since_reg = request.user.hours_since_registration
        hours_remaining = 24 - hours_since_reg
        payment_expired = hours_remaining <= 0 and not request.user.is_verified_payment
        
        # Citas Pendientes para verificar
        pending_appointments = Appointment.objects.filter(business=business, status='PENDING').order_by('-created_at')
        pending_count = pending_appointments.count()
        
    except:
        return redirect('register_owner') # Si no tiene perfil, reenviar a registro

    return render(request, 'businesses/dashboard.html', {
        'pending_appointments': pending_appointments,
        'pending_count': pending_count,
        'hours_remaining': max(0, int(hours_remaining)),
        'payment_expired': payment_expired
    })

# ... (Mantener las otras vistas services_list, etc) ...
# Para asegurar que no se borren, incluimos los placeholders funcionales
@login_required
def services_list(request): return render(request, 'businesses/services.html')
@login_required
def employees_list(request): return render(request, 'businesses/employees.html')
@login_required
def schedule_config(request): return render(request, 'businesses/schedule.html')
@login_required
def business_settings(request): return render(request, 'businesses/settings.html')
