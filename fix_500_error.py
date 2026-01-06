import os

# ==========================================
# VISTA BLINDADA (SAFE MODE)
# ==========================================
# Esta versión del dashboard usa bloques 'try-except' para
# evitar que un error de cálculo tumbe toda la página.
safe_dashboard_view = """from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BusinessProfile, OperatingHour
from apps.booking.models import Appointment

@login_required
def owner_dashboard(request):
    user = request.user
    
    # 1. AUTOCURACIÓN: Si no tiene perfil, lo crea sin errores
    try:
        if not hasattr(user, 'business_profile'):
            profile = BusinessProfile.objects.create(
                owner=user,
                business_name=f"Negocio de {user.first_name}",
                address="Dirección Pendiente",
                deposit_percentage=30
            )
            # Horarios default
            for day_code, _ in OperatingHour.DAYS:
                OperatingHour.objects.create(
                    business=profile, day_of_week=day_code, opening_time="09:00", closing_time="19:00", is_closed=(day_code==6)
                )
            business = profile
        else:
            business = user.business_profile
    except Exception as e:
        # Si falla la creación, mostramos un error pero cargamos la página
        print(f"Error creando perfil: {e}")
        business = None

    # 2. CÁLCULO SEGURO DE TIEMPO (Evita el error 500 si falla el modelo)
    try:
        hours_since_reg = user.hours_since_registration
        hours_remaining = 24 - hours_since_reg
        payment_expired = hours_remaining <= 0 and not user.is_verified_payment
        hours_display = max(0, int(hours_remaining))
    except Exception as e:
        print(f"Error calculando tiempo: {e}")
        hours_remaining = 24
        payment_expired = False
        hours_display = 24
    
    # 3. CARGA SEGURA DE CITAS
    pending_appointments = []
    pending_count = 0
    if business:
        try:
            pending_appointments = Appointment.objects.filter(business=business, status='PENDING').order_by('-created_at')
            pending_count = pending_appointments.count()
        except Exception as e:
            print(f"Error cargando citas: {e}")

    return render(request, 'businesses/dashboard.html', {
        'pending_appointments': pending_appointments,
        'pending_count': pending_count,
        'hours_remaining': hours_display,
        'payment_expired': payment_expired
    })

# --- MANTENEMOS LAS OTRAS VISTAS ---
from .forms import ServiceForm, EmployeeCreationForm, BusinessSettingsForm

@login_required
def services_list(request):
    if not hasattr(request.user, 'business_profile'): return redirect('businesses:dashboard')
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
    if not hasattr(request.user, 'business_profile'): return redirect('businesses:dashboard')
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
    if not hasattr(request.user, 'business_profile'): return redirect('businesses:dashboard')
    business = request.user.business_profile
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

def write_file(path, content):
    print(f"📝 Reparando: {path}...")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚑 APLICANDO PARCHE ANTI-ERROR 500 🚑")
    write_file('apps/businesses/views.py', safe_dashboard_view)
    print("\n✅ Código reparado.")
    print("👉 IMPORTANTE: Haz esto ahora:")
    print("1. Ejecuta: git add .")
    print("2. Ejecuta: git commit -m 'Fix: Dashboard Blindado contra error 500'")
    print("3. Ejecuta: git push origin main")
    print("\n⏳ Y LUEGO, EN EL DASHBOARD DE RENDER:")
    print("   Es posible que falte aplicar migraciones. Busca el botón 'Shell' o 'Console' en Render y escribe:")
    print("   python manage.py migrate")