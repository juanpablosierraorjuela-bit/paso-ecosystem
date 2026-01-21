from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.utils import timezone
import calendar
from apps.core.models import User
from apps.marketplace.models import Appointment
from .models import Service, Salon, EmployeeSchedule
from .forms import ServiceForm, EmployeeCreationForm, OwnerUpdateForm, EmployeeScheduleUpdateForm

@login_required
def employee_dashboard(request):
    if request.user.role != 'EMPLOYEE': return redirect('dashboard')
    
    hoy = timezone.localtime(timezone.now()).date()
    mes = int(request.GET.get('month', hoy.month))
    anio = int(request.GET.get('year', hoy.year))
    
    # Citas del mes
    appointments = Appointment.objects.filter(employee=request.user, status='VERIFIED', date_time__year=anio, date_time__month=mes)
    
    schedule, _ = EmployeeSchedule.objects.get_or_create(employee=request.user)
    
    # Inicializar Formularios
    profile_form = OwnerUpdateForm(instance=request.user)
    password_form = SetPasswordForm(user=request.user)
    schedule_form = EmployeeScheduleUpdateForm(instance=schedule)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = OwnerUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Perfil y usuario actualizados.")
                return redirect('employee_dashboard')
        
        elif 'change_password' in request.POST:
            password_form = SetPasswordForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Contraseña cambiada con éxito.")
                return redirect('employee_dashboard')

        elif 'update_schedule' in request.POST:
            schedule_form = EmployeeScheduleUpdateForm(request.POST, instance=schedule)
            if schedule_form.is_valid():
                schedule_form.save()
                messages.success(request, "Horario actualizado.")
                return redirect('employee_dashboard')

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'schedule_form': schedule_form,
        'appointments': appointments,
        'salon': request.user.workplace,
    }
    return render(request, 'businesses/employee_dashboard.html', context)

# Aquí irían las demás vistas de OWNER (dashboard, services_list, etc) manteniendo su lógica original...
