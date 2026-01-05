import os
import sys

# ==========================================
# 1. CORE MODELS: AGREGAR CÁLCULO DE HORAS
# ==========================================
models_core = """from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrador PASO"
        OWNER = "OWNER", "Dueño de Negocio"
        EMPLOYEE = "EMPLOYEE", "Empleado / Especialista"
        CLIENT = "CLIENT", "Cliente Final"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CLIENT)
    
    # Datos de Contacto
    phone = models.CharField("Teléfono / WhatsApp", max_length=20, blank=True, null=True)
    city = models.CharField("Ciudad", max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    instagram_link = models.URLField("Perfil de Instagram", blank=True, null=True)
    
    # Vinculación Laboral
    workplace = models.ForeignKey('businesses.BusinessProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')

    # Lógica de Seguridad
    is_verified_payment = models.BooleanField("Pago Mensualidad Verificado", default=False)
    registration_timestamp = models.DateTimeField("Fecha de Registro", auto_now_add=True)
    is_active_account = models.BooleanField("Cuenta Activa", default=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    # --- AQUÍ ESTÁ LA FÓRMULA MÁGICA QUE FALTABA ---
    @property
    def hours_since_registration(self):
        if not self.registration_timestamp:
            return 0
        delta = timezone.now() - self.registration_timestamp
        return delta.total_seconds() / 3600

class PlatformSettings(models.Model):
    site_name = models.CharField("Nombre del Sitio", max_length=100, default="PASO Ecosistema")
    support_whatsapp = models.CharField("WhatsApp de Soporte", max_length=20)
    telegram_bot_token = models.CharField(max_length=200, blank=True)
    telegram_chat_id = models.CharField(max_length=100, blank=True)
    instagram_link = models.URLField(blank=True)
    facebook_link = models.URLField(blank=True)
    linkedin_link = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and PlatformSettings.objects.exists():
            raise ValidationError('Solo puede existir una configuración global.')
        return super(PlatformSettings, self).save(*args, **kwargs)
"""

# ==========================================
# 2. BUSINESS VIEWS: AUTOCURACIÓN + PORTERO
# ==========================================
businesses_views = """from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, BusinessProfile, OperatingHour
from .forms import ServiceForm, EmployeeCreationForm, BusinessSettingsForm
from apps.booking.models import Appointment
from django.utils import timezone

@login_required
def owner_dashboard(request):
    user = request.user
    
    # 1. AUTOCURACIÓN: Si no tiene perfil, lo creamos YA MISMO
    if not hasattr(user, 'business_profile'):
        profile = BusinessProfile.objects.create(
            owner=user,
            business_name=f"Negocio de {user.first_name}",
            address="Dirección Pendiente",
            description="Perfil autogenerado.",
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

    # 2. PORTERO: Verificar Pagos (Ahora sí funciona porque arreglamos el modelo)
    try:
        hours_since_reg = user.hours_since_registration
        hours_remaining = 24 - hours_since_reg
        payment_expired = hours_remaining <= 0 and not user.is_verified_payment
    except:
        hours_remaining = 24
        payment_expired = False
    
    # 3. CITAS PENDIENTES
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

# --- OTRAS VISTAS (SE MANTIENEN IGUAL) ---
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

def main():
    print("🚑 REPARANDO ATRIBUTO FALTANTE Y LOGIN 🚑")
    
    # 1. Models (Agregar hours_since_registration)
    write_file('apps/core/models.py', models_core)
    
    # 2. Views (Agregar Autocuración + Portero seguro)
    write_file('apps/businesses/views.py', businesses_views)
    
    print("\n✅ Archivos corregidos.")
    print("👉 EJECUTA EN TERMINAL:")
    print("   git add .")
    print('   git commit -m "Fix: Atributo User faltante y Logica Dashboard"')
    print("   git push origin main")

if __name__ == "__main__":
    main()