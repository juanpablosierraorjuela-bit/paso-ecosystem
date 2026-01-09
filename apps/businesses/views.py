from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from apps.core.models import GlobalSettings, User
from .models import Service, Salon
from .forms import ServiceForm, EmployeeCreationForm, SalonScheduleForm

# --- DASHBOARD PRINCIPAL ---
@login_required
def owner_dashboard(request):
    if request.user.role != 'OWNER':
        return redirect('home')
    
    try:
        salon = request.user.owned_salon
    except:
        return redirect('register_owner')

    # Lógica Timer
    elapsed_time = timezone.now() - request.user.registration_timestamp
    time_limit = timedelta(hours=24)
    remaining_time = time_limit - elapsed_time
    total_seconds_left = max(0, int(remaining_time.total_seconds()))

    # WhatsApp
    admin_settings = GlobalSettings.objects.first()
    admin_phone = admin_settings.whatsapp_support if admin_settings else '573000000000'
    wa_link = f"https://wa.me/{admin_phone}?text=Hola PASO, soy el negocio {salon.name} (ID {request.user.id}). Adjunto pago."

    # Métricas Rápidas
    service_count = salon.services.count()
    employee_count = salon.employees.count()

    context = {
        'salon': salon,
        'seconds_left': total_seconds_left,
        'wa_link': wa_link,
        'is_trial': not request.user.is_verified_payment,
        'service_count': service_count,
        'employee_count': employee_count,
    }
    return render(request, 'businesses/dashboard.html', context)

# --- GESTIÓN DE SERVICIOS ---
@login_required
def services_list(request):
    salon = request.user.owned_salon
    services = salon.services.all()
    
    if request.method == 'POST':
        # Agregar Nuevo Servicio
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.salon = salon
            service.save()
            messages.success(request, "Servicio creado exitosamente.")
            return redirect('services_list')
    else:
        form = ServiceForm()

    return render(request, 'businesses/services.html', {'services': services, 'form': form})

@login_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk, salon=request.user.owned_salon)
    service.delete()
    messages.success(request, "Servicio eliminado.")
    return redirect('services_list')

# --- GESTIÓN DE EMPLEADOS ---
@login_required
def employees_list(request):
    salon = request.user.owned_salon
    employees = salon.employees.all()
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            # Crear Usuario
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone'],
                role='EMPLOYEE',
                workplace=salon,
                is_verified_payment=True # Empleados no pagan
            )
            messages.success(request, f"Empleado {user.first_name} creado.")
            return redirect('employees_list')
    else:
        form = EmployeeCreationForm()

    return render(request, 'businesses/employees.html', {'employees': employees, 'form': form})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(User, pk=pk, workplace=request.user.owned_salon)
    employee.delete() # Ojo: Esto borra el usuario. Podrías solo quitarle el workplace.
    messages.success(request, "Empleado eliminado.")
    return redirect('employees_list')

# --- CONFIGURACIÓN DEL NEGOCIO (HORARIOS) ---
@login_required
def settings_view(request):
    salon = request.user.owned_salon
    if request.method == 'POST':
        form = SalonScheduleForm(request.POST, instance=salon)
        if form.is_valid():
            form.save()
            messages.success(request, "Horarios actualizados.")
            return redirect('settings_view')
    else:
        form = SalonScheduleForm(instance=salon)
    
    return render(request, 'businesses/settings.html', {'form': form, 'salon': salon})