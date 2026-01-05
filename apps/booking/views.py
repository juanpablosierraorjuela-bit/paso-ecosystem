from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Appointment

@login_required
def employee_dashboard(request):
    # Buscamos citas donde el empleado sea el usuario actual
    # Y que estén VERIFICADAS (pagas)
    appointments = Appointment.objects.filter(
        employee=request.user,
        status='VERIFIED'
    ).order_by('date', 'start_time')
    
    return render(request, 'booking/employee_dashboard.html', {'appointments': appointments})

@login_required
def client_dashboard(request):
    return render(request, 'booking/client_dashboard.html')
