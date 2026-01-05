from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, BusinessProfile, OperatingHour
from .forms import ServiceForm, EmployeeCreationForm, BusinessSettingsForm
from apps.core.models import User

@login_required
def owner_dashboard(request):
    return render(request, 'businesses/dashboard.html')

@login_required
def services_list(request):
    business = request.user.business_profile
    services = business.services.all()
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.business = business
            service.save()
            messages.success(request, 'Servicio creado.')
            return redirect('businesses:services')
    else:
        form = ServiceForm()
    return render(request, 'businesses/services.html', {'services': services, 'form': form})

@login_required
def employees_list(request):
    business = request.user.business_profile
    employees = business.staff.all()
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.workplace = business
            employee.save()
            messages.success(request, 'Empleado registrado.')
            return redirect('businesses:employees')
    else:
        form = EmployeeCreationForm()
    return render(request, 'businesses/employees.html', {'employees': employees, 'form': form})

@login_required
def schedule_config(request):
    business = request.user.business_profile
    # Asegurar que existan los 7 días
    if not business.operating_hours.exists():
        for day_code, _ in OperatingHour.DAYS:
            OperatingHour.objects.create(business=business, day_of_week=day_code, opening_time="09:00", closing_time="18:00")
            
    hours = business.operating_hours.all().order_by('day_of_week')
    
    if request.method == 'POST':
        # Lógica simple para guardar cambios (se puede mejorar con Formsets)
        for hour in hours:
            prefix = f"day_{hour.day_of_week}"
            if f"{prefix}_open" in request.POST:
                hour.opening_time = request.POST.get(f"{prefix}_open")
                hour.closing_time = request.POST.get(f"{prefix}_close")
                hour.is_closed = request.POST.get(f"{prefix}_closed") == 'on'
                hour.save()
        messages.success(request, 'Horario actualizado correctamente.')
        return redirect('businesses:schedule')
        
    return render(request, 'businesses/schedule.html', {'hours': hours})

@login_required
def business_settings(request):
    business = request.user.business_profile
    if request.method == 'POST':
        form = BusinessSettingsForm(request.POST, instance=business)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada.')
            return redirect('businesses:settings')
    else:
        form = BusinessSettingsForm(instance=business)
    return render(request, 'businesses/settings.html', {'form': form})
