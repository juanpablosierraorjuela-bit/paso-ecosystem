import os
import subprocess
import sys

# ==========================================
# 1. ACTUALIZAR MODELO USER (VINCULAR EMPLEADOS)
# ==========================================
# Agregamos el campo 'workplace' para saber en qué negocio trabaja el empleado
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
    
    # --- Datos de Contacto ---
    phone = models.CharField("Teléfono / WhatsApp", max_length=20, blank=True, null=True)
    city = models.CharField("Ciudad", max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    instagram_link = models.URLField("Perfil de Instagram", blank=True, null=True)
    
    # --- Vinculación Laboral (NUEVO) ---
    # Si es empleado, aquí guardamos a qué negocio pertenece
    workplace = models.ForeignKey('businesses.BusinessProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')

    # --- Lógica de Seguridad ---
    is_verified_payment = models.BooleanField("Pago Mensualidad Verificado", default=False)
    registration_timestamp = models.DateTimeField("Fecha de Registro", auto_now_add=True)
    is_active_account = models.BooleanField("Cuenta Activa", default=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

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
# 2. CREAR FORMULARIOS (FORMS.PY)
# ==========================================
forms_businesses = """from django import forms
from .models import Service
from apps.core.models import User

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'buffer_minutes', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Corte Clásico'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Descripción para el buscador...'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Minutos'}),
            'buffer_minutes': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Tiempo de limpieza'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Precio COP'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Contraseña'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'instagram_link', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Apellido'}),
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Usuario de Acceso'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email (Opcional)'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'WhatsApp'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://instagram.com/...'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.EMPLOYEE
        if commit:
            user.save()
        return user
"""

# ==========================================
# 3. ACTUALIZAR VISTAS (LOGICA REAL)
# ==========================================
views_businesses = """from django.shortcuts import render, redirect, get_object_or_404
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
"""

# ==========================================
# 4. TEMPLATES (DISEÑO MODERNO)
# ==========================================

# SERVICIOS HTML
services_html = """{% extends 'businesses/base_dashboard.html' %}
{% block dashboard_content %}
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <h1 style="color: #d4af37;">✂️ Mis Servicios</h1>
    <button onclick="document.getElementById('modal-service').style.display='flex'" class="btn btn-primary">
        + Nuevo Servicio
    </button>
</div>

<div style="overflow-x: auto;">
    <table style="width: 100%; border-collapse: collapse; color: #eee;">
        <thead>
            <tr style="border-bottom: 1px solid #444; text-align: left;">
                <th style="padding: 15px;">Nombre</th>
                <th style="padding: 15px;">Precio</th>
                <th style="padding: 15px;">Duración</th>
                <th style="padding: 15px;">Estado</th>
            </tr>
        </thead>
        <tbody>
            {% for service in services %}
            <tr style="border-bottom: 1px solid #222;">
                <td style="padding: 15px;">
                    <strong>{{ service.name }}</strong><br>
                    <small style="color: #888;">{{ service.description|truncatechars:50 }}</small>
                </td>
                <td style="padding: 15px; color: #4cd137;">${{ service.price }}</td>
                <td style="padding: 15px;">{{ service.duration_minutes }} min (+{{ service.buffer_minutes }} lim)</td>
                <td style="padding: 15px;">
                    {% if service.is_active %}
                        <span style="background: rgba(76, 209, 55, 0.2); color: #4cd137; padding: 5px 10px; border-radius: 20px; font-size: 0.8rem;">Activo</span>
                    {% else %}
                        <span style="background: rgba(255, 77, 77, 0.2); color: #ff4d4d; padding: 5px 10px; border-radius: 20px; font-size: 0.8rem;">Inactivo</span>
                    {% endif %}
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="4" style="text-align: center; padding: 40px; color: #888;">
                    No has creado servicios aún. ¡Dale vida a tu negocio!
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<div id="modal-service" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 2000;">
    <div style="background: #111; padding: 30px; border-radius: 10px; border: 1px solid #333; width: 500px; max-width: 90%;">
        <h2 style="margin-bottom: 20px; color: #d4af37;">Crear Servicio</h2>
        <form method="post">
            {% csrf_token %}
            {{ form.as_p }}
            <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: flex-end;">
                <button type="button" onclick="document.getElementById('modal-service').style.display='none'" class="btn btn-outline" style="border: none; color: #888;">Cancelar</button>
                <button type="submit" class="btn btn-primary">Guardar</button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
"""

# EMPLEADOS HTML
employees_html = """{% extends 'businesses/base_dashboard.html' %}
{% block dashboard_content %}
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <h1 style="color: #d4af37;">👥 Mi Equipo</h1>
    <button onclick="document.getElementById('modal-employee').style.display='flex'" class="btn btn-primary">
        + Nuevo Empleado
    </button>
</div>

<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px;">
    {% for employee in employees %}
    <div style="background: #111; padding: 20px; border-radius: 10px; border: 1px solid #333; text-align: center;">
        <div style="width: 60px; height: 60px; background: linear-gradient(45deg, #d4af37, #b5952f); border-radius: 50%; margin: 0 auto 15px; display: flex; justify-content: center; align-items: center; color: black; font-weight: bold; font-size: 1.5rem;">
            {{ employee.first_name|first }}{{ employee.last_name|first }}
        </div>
        <h3 style="margin-bottom: 5px;">{{ employee.first_name }} {{ employee.last_name }}</h3>
        <p style="color: #888; font-size: 0.9rem;">@{{ employee.username }}</p>
        <div style="margin-top: 15px;">
            <span style="font-size: 0.8rem; background: #222; padding: 5px 10px; border-radius: 10px; border: 1px solid #444;">
                {{ employee.phone|default:"Sin teléfono" }}
            </span>
        </div>
    </div>
    {% empty %}
    <p style="color: #888; grid-column: 1/-1; text-align: center;">Aún no tienes empleados. Agrega uno para empezar.</p>
    {% endfor %}
</div>

<div id="modal-employee" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 2000;">
    <div style="background: #111; padding: 30px; border-radius: 10px; border: 1px solid #333; width: 500px; max-width: 90%;">
        <h2 style="margin-bottom: 20px; color: #d4af37;">Registrar Empleado</h2>
        <form method="post">
            {% csrf_token %}
            {{ form.as_p }}
            <p style="font-size: 0.8rem; color: #666; margin-top: 10px;">* El empleado podrá iniciar sesión con este usuario y contraseña.</p>
            <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: flex-end;">
                <button type="button" onclick="document.getElementById('modal-employee').style.display='none'" class="btn btn-outline" style="border: none; color: #888;">Cancelar</button>
                <button type="submit" class="btn btn-primary">Crear Acceso</button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 5. UTILS
# ==========================================
def write_file(path, content):
    print(f"📝 Escribiendo: {path}...")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def run_command(command):
    print(f"🚀 Ejecutando: {command}")
    subprocess.run(command, shell=True, check=True)

def main():
    print("🚧 CONSTRUYENDO MÓDULOS DE NEGOCIO (SERVICIOS + EMPLEADOS) 🚧")
    
    # 1. Models
    write_file('apps/core/models.py', models_core)
    
    # 2. Forms
    write_file('apps/businesses/forms.py', forms_businesses)
    
    # 3. Views
    write_file('apps/businesses/views.py', views_businesses)
    
    # 4. Templates
    write_file('templates/businesses/services.html', services_html)
    write_file('templates/businesses/employees.html', employees_html)
    
    # 5. Migraciones y Deploy
    print("\n📦 Aplicando cambios a la Base de Datos...")
    run_command("python manage.py makemigrations")
    run_command("python manage.py migrate")
    
    print("\n☁️ Subiendo a Render...")
    try:
        run_command("git add .")
        run_command('git commit -m "Feat: Modulos Servicios y Empleados Funcionales"')
        run_command("git push origin main")
        print("\n✅ ¡Misión Cumplida! Ve a tu Panel -> Servicios y empieza a crear.")
    except Exception as e:
        print(f"⚠️ Error Git: {e}")
        
    try:
        os.remove(sys.argv[0])
    except:
        pass

if __name__ == "__main__":
    main()