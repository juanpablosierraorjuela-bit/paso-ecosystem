import os
import subprocess
import sys

# ==========================================
# 1. BUSINESSES VIEWS: AUTOCURACIÓN (SELF-HEALING)
# ==========================================
# Esta es la joya. Si el perfil no existe, lo crea al vuelo.
businesses_views_fixed = """from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, BusinessProfile, OperatingHour
from .forms import ServiceForm, EmployeeCreationForm, BusinessSettingsForm
from apps.booking.models import Appointment
from django.utils import timezone

@login_required
def owner_dashboard(request):
    # --- LÓGICA DE AUTOCURACIÓN (SELF-HEALING) ---
    # Si el usuario llega aquí y no tiene perfil, lo creamos en lugar de expulsarlo.
    if not hasattr(request.user, 'business_profile'):
        profile = BusinessProfile.objects.create(
            owner=request.user,
            business_name=f"Negocio de {request.user.first_name}",
            address="Dirección Pendiente",
            description="Perfil autogenerado por el sistema.",
            deposit_percentage=30
        )
        # Crear horarios por defecto para evitar errores en calendario
        for day_code, _ in OperatingHour.DAYS:
            OperatingHour.objects.create(
                business=profile,
                day_of_week=day_code,
                opening_time="09:00",
                closing_time="19:00",
                is_closed=(day_code == 6)
            )
        messages.info(request, "¡Perfil de negocio restaurado automáticamente!")
        business = profile
    else:
        business = request.user.business_profile

    # --- LÓGICA DEL PORTERO (24H REAPER) ---
    hours_since_reg = request.user.hours_since_registration
    hours_remaining = 24 - hours_since_reg
    payment_expired = hours_remaining <= 0 and not request.user.is_verified_payment
    
    # Citas Pendientes
    try:
        pending_appointments = Appointment.objects.filter(business=business, status='PENDING').order_by('-created_at')
        pending_count = pending_appointments.count()
    except:
        pending_appointments = []
        pending_count = 0

    return render(request, 'businesses/dashboard.html', {
        'pending_appointments': pending_appointments,
        'pending_count': pending_count,
        'hours_remaining': max(0, int(hours_remaining)),
        'payment_expired': payment_expired
    })

# --- VISTAS DEL NEGOCIO (SERVICIOS, EMPLEADOS, ETC) ---
@login_required
def services_list(request):
    # Verificación de seguridad
    if not hasattr(request.user, 'business_profile'): return redirect('businesses:dashboard')
    
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
    if not hasattr(request.user, 'business_profile'): return redirect('businesses:dashboard')
    
    business = request.user.business_profile
    employees = business.staff.all()
    
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
    if not hasattr(request.user, 'business_profile'): return redirect('businesses:dashboard')
    
    business = request.user.business_profile
    # Autocuración de horarios
    if not business.operating_hours.exists():
        for day_code, _ in OperatingHour.DAYS:
            OperatingHour.objects.create(business=business, day_of_week=day_code, opening_time="09:00", closing_time="18:00")
            
    hours = business.operating_hours.all().order_by('day_of_week')
    
    if request.method == 'POST':
        for hour in hours:
            prefix = f"day_{hour.day_of_week}"
            if f"{prefix}_open" in request.POST:
                hour.opening_time = request.POST.get(f"{prefix}_open")
                hour.closing_time = request.POST.get(f"{prefix}_close")
                hour.is_closed = request.POST.get(f"{prefix}_closed") == 'on'
                hour.save()
        messages.success(request, 'Horario actualizado.')
        return redirect('businesses:schedule')
        
    return render(request, 'businesses/schedule.html', {'hours': hours})

@login_required
def business_settings(request):
    if not hasattr(request.user, 'business_profile'): return redirect('businesses:dashboard')
    
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
"""

# ==========================================
# 2. CORE VIEWS: REGISTRO BLINDADO
# ==========================================
# Aseguramos que los nuevos registros SIEMPRE creen el negocio desde el principio
core_views_fixed = """from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from .forms import OwnerRegistrationForm
from django.urls import reverse_lazy
from .models import User
from apps.businesses.models import BusinessProfile, OperatingHour

def pain_landing(request):
    return render(request, 'landing/pain_points.html')

class OwnerRegisterView(CreateView):
    model = User
    form_class = OwnerRegistrationForm
    template_name = 'registration/register_owner.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = User.Role.OWNER
        user.save()
        
        # BLINDAJE: Crear perfil inmediatamente
        if not hasattr(user, 'business_profile'):
            biz_name = form.cleaned_data.get('business_name', f"Negocio de {user.first_name}")
            address = form.cleaned_data.get('address', "Dirección pendiente")
            
            profile = BusinessProfile.objects.create(
                owner=user,
                business_name=biz_name,
                address=address
            )
            # Crear horarios
            for day_code, _ in OperatingHour.DAYS:
                OperatingHour.objects.create(business=profile, day_of_week=day_code, opening_time="09:00", closing_time="19:00", is_closed=(day_code==6))
                
        return super().form_valid(form)

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard_redirect(request):
    user = request.user
    if user.role == User.Role.OWNER:
        return redirect('businesses:dashboard')
    elif user.role == User.Role.EMPLOYEE:
        return redirect('booking:employee_dashboard')
    elif user.role == User.Role.CLIENT:
        return redirect('booking:client_dashboard')
    elif user.is_staff:
        return redirect('/admin/')
    return redirect('home')
"""

# ==========================================
# 3. UTILS
# ==========================================
def write_file(path, content):
    print(f"📝 Reparando: {path}...")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"❌ Error: {e}")

def run_command(command):
    print(f"🚀 Ejecutando: {command}")
    subprocess.run(command, shell=True, check=True)

def main():
    print("🚑 APLICANDO PARCHE DE BUCLE INFINITO 🚑")
    
    # 1. Dashboard Autocurable
    write_file('apps/businesses/views.py', businesses_views_fixed)
    
    # 2. Registro Blindado
    write_file('apps/core/views.py', core_views_fixed)
    
    print("\n✅ Código reparado.")
    print("👉 Ejecuta ahora:")
    print("   git add .")
    print('   git commit -m "Fix: Bucle Infinito y Autocuracion de Perfil"')
    print("   git push origin main")

if __name__ == "__main__":
    main()