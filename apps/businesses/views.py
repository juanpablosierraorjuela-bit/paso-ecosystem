from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Salon, Service, EmployeeSchedule
from apps.core.models import User, GlobalSettings
from .forms import ServiceForm, EmployeeCreationForm, SalonSettingsForm

@login_required
def owner_dashboard(request):
    if request.user.role != 'OWNER': return redirect('home')
    salon = request.user.salon
    
    # Lógica del Reaper (Pago)
    hours_since = request.user.hours_since_registration()
    hours_remaining = max(0, int(24 - hours_since))
    is_verified = request.user.is_verified_payment
    
    # Datos para el template
    context = {
        'salon': salon,
        'hours_remaining': hours_remaining,
        'is_verified': is_verified,
        'services_count': salon.services.count(),
        'employees_count': salon.staff.count(),
    }
    return render(request, 'businesses/dashboard.html', context)

@login_required
def services_list(request):
    salon = request.user.salon
    services = salon.services.all()
    
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.salon = salon
            service.save()
            messages.success(request, "Servicio creado con éxito.")
            return redirect('businesses:services')
    else:
        form = ServiceForm()
    
    return render(request, 'businesses/services.html', {'services': services, 'form': form})

@login_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk, salon=request.user.salon)
    service.delete()
    messages.success(request, "Servicio eliminado.")
    return redirect('businesses:services')

@login_required
def employees_list(request):
    salon = request.user.salon
    employees = salon.staff.all()
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.workplace = salon
            user.save()
            # Crear horario por defecto
            EmployeeSchedule.objects.create(employee=user)
            messages.success(request, "Empleado registrado.")
            return redirect('businesses:employees')
    else:
        form = EmployeeCreationForm()
        
    return render(request, 'businesses/employees.html', {'employees': employees, 'form': form})

@login_required
def settings_view(request):
    salon = request.user.salon
    if request.method == 'POST':
        form = SalonSettingsForm(request.POST, instance=salon)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración guardada.")
            return redirect('businesses:settings')
    else:
        form = SalonSettingsForm(instance=salon)
    return render(request, 'businesses/settings.html', {'form': form, 'salon': salon})