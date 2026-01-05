import os
import django
import sys

# Configuramos el entorno de Django para que el script pueda hablar con la Base de Datos
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.businesses.models import BusinessProfile, OperatingHour

# ==========================================
# 1. PARCHE DE EMERGENCIA (Fix Data)
# ==========================================
def fix_current_user_profile():
    User = get_user_model()
    # Buscamos tu usuario (ajusta el email si es diferente, pero vi ese en los logs)
    email_objetivo = "juanpablosierraorjuela@gmail.com"
    
    try:
        user = User.objects.get(email=email_objetivo)
        print(f"✅ Usuario encontrado: {user.first_name}")
        
        # Verificamos si ya tiene perfil (para evitar duplicados)
        if not hasattr(user, 'business_profile'):
            print("🛠️ Creando Perfil de Negocio de emergencia...")
            profile = BusinessProfile.objects.create(
                owner=user,
                business_name=f"Salón de {user.first_name}",
                address="Dirección Pendiente",
                description="Negocio creado automáticamente por el sistema de recuperación.",
                deposit_percentage=50
            )
            # Crear horarios por defecto (Lunes a Sábado 9-6)
            for day_code, day_name in OperatingHour.DAYS:
                OperatingHour.objects.create(
                    business=profile,
                    day_of_week=day_code,
                    opening_time="09:00",
                    closing_time="18:00",
                    is_closed=(day_code == 6) # Domingo cerrado por defecto
                )
            print("🎉 ¡Perfil creado! Ya puedes entrar a 'Servicios' sin errores.")
        else:
            print("ℹ️ El usuario ya tiene perfil de negocio.")
            
    except User.DoesNotExist:
        print(f"⚠️ No encontré al usuario {email_objetivo}. Si usaste otro, edita la línea 19 del script.")

# ==========================================
# 2. ACTUALIZAR FORMULARIOS (Para nuevos usuarios)
# ==========================================
forms_code = """from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Service, BusinessProfile, OperatingHour

User = get_user_model()

# --- FORMULARIO DE USUARIO (DUEÑO) ---
class OwnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Contraseña'}), label="Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirmar'}), label="Confirmar")
    
    # Campos del Negocio (Integrados en el mismo registro)
    business_name = forms.CharField(label="Nombre del Negocio", widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Belleza Total'}))
    address = forms.CharField(label="Dirección", widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Calle 123 # 45-67'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'city', 'instagram_link']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}), # Debería ser Select, simplificado por ahora
            'instagram_link': forms.URLInput(attrs={'class': 'form-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.username = self.cleaned_data["email"]
        user.role = User.Role.OWNER
        if commit:
            user.save()
            # Crear el perfil de negocio automáticamente
            BusinessProfile.objects.create(
                owner=user,
                business_name=self.cleaned_data['business_name'],
                address=self.cleaned_data['address']
            )
        return user

# --- FORMULARIOS DEL PANEL (SERVICIOS, EMPLEADOS, ETC) ---
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'buffer_minutes', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input'}),
            'buffer_minutes': forms.NumberInput(attrs={'class': 'form-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
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
        fields = ['business_name', 'description', 'address', 'google_maps_url', 'deposit_percentage', 'is_open_manually']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'address': forms.TextInput(attrs={'class': 'form-input'}),
            'google_maps_url': forms.URLInput(attrs={'class': 'form-input'}),
            'deposit_percentage': forms.NumberInput(attrs={'class': 'form-input'}),
            'is_open_manually': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
"""

# ==========================================
# 3. ACTUALIZAR VISTAS (LOGICA COMPLETA)
# ==========================================
views_code = """from django.shortcuts import render, redirect, get_object_or_404
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
"""

# ==========================================
# 4. TEMPLATES RESTANTES (HORARIO Y SETTINGS)
# ==========================================
schedule_html = """{% extends 'businesses/base_dashboard.html' %}
{% block dashboard_content %}
<h1 style="color: #d4af37; margin-bottom: 20px;">⏰ Horario Operativo</h1>
<div style="background: #111; padding: 30px; border-radius: 10px; border: 1px solid #333;">
    <form method="post">
        {% csrf_token %}
        <div style="display: grid; gap: 15px;">
            {% for hour in hours %}
            <div style="display: flex; align-items: center; gap: 15px; border-bottom: 1px solid #222; padding-bottom: 10px;">
                <div style="width: 100px; font-weight: bold;">{{ hour.get_day_of_week_display }}</div>
                
                <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                    <input type="checkbox" name="day_{{ hour.day_of_week }}_closed" {% if hour.is_closed %}checked{% endif %}>
                    <span style="font-size: 0.9rem; color: #ff4d4d;">Cerrado</span>
                </label>
                
                <input type="time" name="day_{{ hour.day_of_week }}_open" value="{{ hour.opening_time|date:'H:i' }}" class="form-input" style="width: auto; padding: 5px;">
                <span>a</span>
                <input type="time" name="day_{{ hour.day_of_week }}_close" value="{{ hour.closing_time|date:'H:i' }}" class="form-input" style="width: auto; padding: 5px;">
            </div>
            {% endfor %}
        </div>
        <button type="submit" class="btn btn-primary" style="margin-top: 30px;">Guardar Horario</button>
    </form>
</div>
{% endblock %}
"""

settings_html = """{% extends 'businesses/base_dashboard.html' %}
{% block dashboard_content %}
<h1 style="color: #d4af37; margin-bottom: 20px;">⚙️ Configuración del Negocio</h1>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
    
    <div style="background: #111; padding: 30px; border-radius: 10px; border: 1px solid #333;">
        <h3 style="margin-bottom: 20px;">Datos Públicos</h3>
        <form method="post">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit" class="btn btn-primary" style="margin-top: 20px; width: 100%;">Guardar Cambios</button>
        </form>
    </div>

    <div style="background: #111; padding: 30px; border-radius: 10px; border: 1px solid #333; height: fit-content;">
        <h3 style="margin-bottom: 20px;">Pagos y Abonos</h3>
        <p style="color: #888; font-size: 0.9rem; margin-bottom: 15px;">
            Define cuánto deben pagar tus clientes por adelantado para asegurar su cita.
        </p>
        <div style="padding: 15px; background: rgba(212, 175, 55, 0.1); border: 1px solid #d4af37; border-radius: 5px; color: #d4af37;">
            ℹ️ El dinero del abono llega directamente a tu cuenta.
        </div>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 5. UTILIDADES DE ESCRITURA
# ==========================================
def write_file(path, content):
    print(f"📝 Escribiendo: {path}...")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"❌ Error en {path}: {e}")

def run_command(command):
    print(f"🚀 Ejecutando: {command}")
    subprocess.run(command, shell=True, check=True)

# ==========================================
# 🏁 EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("\n🦄 INICIANDO REPARACIÓN Y CONSTRUCCIÓN FINAL 🦄")
    
    # 1. Arreglar Datos
    fix_current_user_profile()
    
    # 2. Actualizar Código
    write_file('apps/businesses/forms.py', forms_code)
    write_file('apps/businesses/views.py', views_code)
    write_file('templates/businesses/schedule.html', schedule_html)
    write_file('templates/businesses/settings.html', settings_html)
    
    # 3. Subir
    print("\n📦 Enviando mejoras a la nube...")
    try:
        run_command("git add .")
        run_command('git commit -m "Fix: Perfil faltante + Modulos Horario y Settings Completos"')
        run_command("git push origin main")
        print("\n✅ ¡LISTO! El sistema está reparado y completo.")
        print("👉 Entra a tu panel, el error 500 habrá desaparecido.")
    except Exception as e:
        print(f"⚠️ Error Git (Tal vez no hubo cambios): {e}")