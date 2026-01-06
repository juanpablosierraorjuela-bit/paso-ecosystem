import os

# ==========================================
# 1. RECUPERAR EL CEREBRO (VIEWS.PY)
# ==========================================
businesses_views = """from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BusinessProfile, OperatingHour
from apps.booking.models import Appointment
from .forms import ServiceForm, EmployeeCreationForm, BusinessSettingsForm

@login_required
def owner_dashboard(request):
    user = request.user
    # 1. AUTOCURACIÓN: Si el usuario es dueño pero no tiene perfil, lo creamos
    try:
        if not hasattr(user, 'business_profile'):
            profile = BusinessProfile.objects.create(
                owner=user,
                business_name=f"Negocio de {user.first_name}",
                address="Dirección Pendiente"
            )
            # Horarios por defecto
            for day_code, _ in OperatingHour.DAYS:
                OperatingHour.objects.create(
                    business=profile, day_of_week=day_code, opening_time="09:00", closing_time="19:00", is_closed=(day_code==6)
                )
            business = profile
        else:
            business = user.business_profile
    except Exception as e:
        print(f"Error recuperando perfil: {e}")
        business = None

    # 2. LOGICA DE PAGO (PORTERO)
    try:
        hours_since_reg = user.hours_since_registration
        hours_remaining = 24 - hours_since_reg
        payment_expired = hours_remaining <= 0 and not user.is_verified_payment
    except:
        hours_remaining = 24
        payment_expired = False

    # 3. CITAS PENDIENTES
    pending_appointments = []
    if business:
        pending_appointments = Appointment.objects.filter(business=business, status='PENDING').order_by('-created_at')

    return render(request, 'businesses/dashboard.html', {
        'pending_appointments': pending_appointments,
        'hours_remaining': max(0, int(hours_remaining)),
        'payment_expired': payment_expired
    })

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
            messages.success(request, 'Servicio agregado correctamente.')
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
# 2. CONECTAR LOS CABLES (URLS.PY)
# ==========================================
businesses_urls = """from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('dashboard/', views.owner_dashboard, name='dashboard'),
    path('services/', views.services_list, name='services'),
    path('employees/', views.employees_list, name='employees'),
    path('schedule/', views.schedule_config, name='schedule'),
    path('settings/', views.business_settings, name='settings'),
    
    # Redirección de compatibilidad
    path('panel/', views.owner_dashboard, name='panel_negocio'),
]
"""

# ==========================================
# 3. RECUPERAR FORMULARIOS (FORMS.PY)
# ==========================================
businesses_forms = """from django import forms
from django.contrib.auth import get_user_model
from .models import Service, BusinessProfile, OperatingHour

User = get_user_model()

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corte Caballero'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.EMPLOYEE
        if commit:
            user.save()
        return user

class BusinessSettingsForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = ['business_name', 'description', 'address', 'deposit_percentage']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'deposit_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }
"""

def write_file(path, content):
    print(f"🚑 Restaurando: {path}...")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔋 INICIANDO PROTOCOLO DE RECUPERACIÓN DE PANEL 🔋")
    write_file('apps/businesses/views.py', businesses_views)
    write_file('apps/businesses/urls.py', businesses_urls)
    write_file('apps/businesses/forms.py', businesses_forms)
    print("\n✅ ¡Todo recuperado! Tu código ha vuelto a la vida.")
    print("👉 EJECUTA AHORA:")
    print("   git add .")
    print("   git commit -m 'Fix: Restauracion total del Panel de Dueño'")
    print("   git push origin main")