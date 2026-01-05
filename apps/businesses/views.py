from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, BusinessProfile
from .forms import ServiceForm, EmployeeCreationForm
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
            messages.success(request, '¡Servicio creado con éxito!')
            return redirect('businesses:services')
    else:
        form = ServiceForm()
    
    return render(request, 'businesses/services.html', {'services': services, 'form': form})

@login_required
def employees_list(request):
    business = request.user.business_profile
    employees = business.staff.all() # Usamos el related_name 'staff' del modelo User
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.workplace = business
            employee.save()
            messages.success(request, f'Empleado {employee.first_name} creado correctamente.')
            return redirect('businesses:employees')
    else:
        form = EmployeeCreationForm()
        
    return render(request, 'businesses/employees.html', {'employees': employees, 'form': form})

@login_required
def schedule_config(request):
    return render(request, 'businesses/schedule.html')

@login_required
def business_settings(request):
    return render(request, 'businesses/settings.html')
