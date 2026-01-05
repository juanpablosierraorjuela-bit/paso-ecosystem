import os
import subprocess
import sys

# ==========================================
# 1. FORMS: VALIDACIÓN DE HORARIOS Y PERFIL
# ==========================================
booking_forms = """from django import forms
from .models import EmployeeSchedule
from apps.core.models import User
from apps.businesses.models import OperatingHour
import datetime

class EmployeeScheduleForm(forms.ModelForm):
    class Meta:
        model = EmployeeSchedule
        fields = ['start_time', 'end_time', 'break_start', 'break_end', 'is_active_day']
    
    def __init__(self, *args, **kwargs):
        self.business_hour = kwargs.pop('business_hour', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        is_active = cleaned_data.get('is_active_day')

        if is_active and self.business_hour:
            # 1. Validar que el negocio esté abierto ese día
            if self.business_hour.is_closed:
                raise forms.ValidationError("No puedes programar turno un día que el negocio está cerrado.")
            
            # 2. Validar rangos (Lógica Cruzada)
            # Nota: Esto es una validación básica, para turnos nocturnos complejos se requiere lógica extra
            if start and start < self.business_hour.opening_time:
                self.add_error('start_time', f"El negocio abre a las {self.business_hour.opening_time}")
            
            if end and end > self.business_hour.closing_time:
                # Si no es turno nocturno
                if not self.business_hour.crosses_midnight():
                    self.add_error('end_time', f"El negocio cierra a las {self.business_hour.closing_time}")

        return cleaned_data

class EmployeeProfileForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Nueva contraseña (opcional)'}),
        required=False,
        label="Cambiar Contraseña"
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'instagram_link', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
"""

# ==========================================
# 2. VIEWS: LÓGICA DE GESTIÓN
# ==========================================
booking_views = """from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment, EmployeeSchedule
from apps.businesses.models import OperatingHour
from .forms import EmployeeScheduleForm, EmployeeProfileForm

@login_required
def employee_dashboard(request):
    # Citas verificadas
    appointments = Appointment.objects.filter(
        employee=request.user,
        status='VERIFIED'
    ).order_by('date', 'start_time')
    return render(request, 'booking/employee_dashboard.html', {'appointments': appointments})

@login_required
def employee_schedule(request):
    employee = request.user
    workplace = employee.workplace
    
    if not workplace:
        messages.error(request, "No tienes un negocio asignado. Contacta a tu jefe.")
        return redirect('booking:employee_dashboard')

    # Asegurar que existan los 7 días de horario para el empleado
    if not employee.schedules.exists():
        for day_code, _ in OperatingHour.DAYS:
            EmployeeSchedule.objects.create(
                employee=employee,
                business=workplace,
                day_of_week=day_code,
                start_time="09:00",
                end_time="18:00"
            )

    # Traemos los horarios del EMPLEADO y del NEGOCIO para cruzar la info
    emp_schedules = employee.schedules.all().order_by('day_of_week')
    biz_hours = workplace.operating_hours.all()
    # Creamos un dict para acceso rápido: biz_hours_map[0] = Horario Lunes
    biz_hours_map = {h.day_of_week: h for h in biz_hours}

    if request.method == 'POST':
        # Procesamiento simple del formulario manual
        for schedule in emp_schedules:
            day = schedule.day_of_week
            
            # Solo procesar si el negocio abre ese día
            if not biz_hours_map.get(day).is_closed:
                prefix = f"day_{day}"
                
                # Checkbox de Activo
                is_active = request.POST.get(f"{prefix}_active") == 'on'
                schedule.is_active_day = is_active
                
                if is_active:
                    schedule.start_time = request.POST.get(f"{prefix}_start")
                    schedule.end_time = request.POST.get(f"{prefix}_end")
                    
                    # Breaks (Opcionales)
                    b_start = request.POST.get(f"{prefix}_break_start")
                    b_end = request.POST.get(f"{prefix}_break_end")
                    if b_start and b_end:
                        schedule.break_start = b_start
                        schedule.break_end = b_end
                    else:
                        schedule.break_start = None
                        schedule.break_end = None
                
                schedule.save()
        
        messages.success(request, "Tu horario ha sido actualizado.")
        return redirect('booking:employee_schedule')

    # Preparamos los datos combinados para el template
    combined_schedule = []
    for emp_sch in emp_schedules:
        biz_h = biz_hours_map.get(emp_sch.day_of_week)
        combined_schedule.append({
            'employee': emp_sch,
            'business': biz_h
        })

    return render(request, 'booking/schedule.html', {'combined_schedule': combined_schedule})

@login_required
def employee_profile(request):
    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('booking:employee_profile')
    else:
        form = EmployeeProfileForm(instance=request.user)
    
    return render(request, 'booking/profile.html', {'form': form})

@login_required
def client_dashboard(request):
    return render(request, 'booking/client_dashboard.html')
"""

# ==========================================
# 3. URLS: RUTAS NUEVAS
# ==========================================
booking_urls = """from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('mi-agenda/', views.employee_dashboard, name='employee_dashboard'),
    path('mi-horario/', views.employee_schedule, name='employee_schedule'),
    path('mi-perfil/', views.employee_profile, name='employee_profile'),
    path('mis-citas/', views.client_dashboard, name='client_dashboard'),
]
"""

# ==========================================
# 4. TEMPLATES: DISEÑO INTELIGENTE
# ==========================================

# 4.1 Dashboard Actualizado (Botones)
dashboard_html = """{% extends 'base.html' %}
{% block content %}
<div style="padding: 100px 5%; color: white;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; flex-wrap: wrap; gap: 20px;">
        <div>
            <h1 style="color: #d4af37;">Hola, {{ user.first_name }}</h1>
            <p style="color: #ccc;">{{ user.workplace.business_name|default:"Sin Negocio Asignado" }}</p>
        </div>
        
        <div style="display: flex; gap: 10px;">
            <a href="{% url 'booking:employee_schedule' %}" class="btn btn-outline" style="border-color: #d4af37; color: #d4af37;">
                ⏰ Configurar Horario
            </a>
            <a href="{% url 'booking:employee_profile' %}" class="btn btn-outline">
                👤 Mi Perfil
            </a>
        </div>
    </div>

    <hr style="border-color: #333; margin-bottom: 30px;">

    <h3 style="margin-bottom: 20px;">📅 Próximas Citas Confirmadas</h3>
    <div style="display: grid; gap: 20px;">
        {% for cita in appointments %}
        <div style="background: #111; border-left: 4px solid #d4af37; padding: 20px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="font-size: 1.2rem; margin-bottom: 5px;">{{ cita.service.name }}</h3>
                <p style="color: #888;">Cliente: <strong style="color: white;">{{ cita.client.first_name }} {{ cita.client.last_name }}</strong></p>
                <p style="color: #888;">Hora: <strong style="color: #d4af37;">{{ cita.start_time|time:"H:i" }} - {{ cita.end_time|time:"H:i" }}</strong></p>
            </div>
            <div>
                <a href="#" class="btn btn-primary" style="font-size: 0.8rem; padding: 5px 15px;">Iniciar</a>
            </div>
        </div>
        {% empty %}
        <div style="text-align: center; padding: 50px; background: #111; border-radius: 10px; border: 1px dashed #333;">
            <h3 style="color: #666;">Agenda Libre 🍃</h3>
            <p style="color: #444;">No hay citas verificadas por el dueño aún.</p>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

# 4.2 Horario Inteligente (Lógica Cruzada Visual)
schedule_html = """{% extends 'base.html' %}
{% block content %}
<div style="padding: 100px 5%; color: white; max-width: 900px; margin: 0 auto;">
    <div style="margin-bottom: 30px;">
        <a href="{% url 'booking:employee_dashboard' %}" style="color: #888; text-decoration: none;">← Volver al Panel</a>
        <h1 style="color: #d4af37; margin-top: 10px;">⏰ Configurar Disponibilidad</h1>
        <p style="color: #ccc;">Ajusta tu horario dentro de los límites del negocio.</p>
    </div>

    <form method="post" style="background: #111; padding: 30px; border-radius: 15px; border: 1px solid #333;">
        {% csrf_token %}
        
        <div style="display: flex; flex-direction: column; gap: 20px;">
            {% for item in combined_schedule %}
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #222; padding-bottom: 15px; flex-wrap: wrap; gap: 15px;">
                
                <div style="min-width: 120px;">
                    <strong style="font-size: 1.1rem; display: block;">{{ item.employee.get_day_of_week_display }}</strong>
                    {% if item.business.is_closed %}
                        <span style="color: #ff4d4d; font-size: 0.8rem;">⛔ Negocio Cerrado</span>
                    {% else %}
                        <span style="color: #4cd137; font-size: 0.8rem;">🟢 Abierto ({{ item.business.opening_time|time:"H:i" }} - {{ item.business.closing_time|time:"H:i" }})</span>
                    {% endif %}
                </div>

                {% if not item.business.is_closed %}
                <div style="display: flex; gap: 20px; align-items: center; flex: 1;">
                    
                    <label style="display: flex; align-items: center; gap: 5px; cursor: pointer;">
                        <input type="checkbox" name="day_{{ item.employee.day_of_week }}_active" {% if item.employee.is_active_day %}checked{% endif %}>
                        <span>Trabajar</span>
                    </label>

                    <div style="display: flex; align-items: center; gap: 5px;">
                        <input type="time" name="day_{{ item.employee.day_of_week }}_start" 
                               value="{{ item.employee.start_time|time:'H:i' }}" 
                               min="{{ item.business.opening_time|time:'H:i' }}" 
                               max="{{ item.business.closing_time|time:'H:i' }}"
                               class="form-input" style="padding: 5px; width: auto;">
                        <span>a</span>
                        <input type="time" name="day_{{ item.employee.day_of_week }}_end" 
                               value="{{ item.employee.end_time|time:'H:i' }}" 
                               min="{{ item.business.opening_time|time:'H:i' }}" 
                               max="{{ item.business.closing_time|time:'H:i' }}"
                               class="form-input" style="padding: 5px; width: auto;">
                    </div>

                    <div style="font-size: 0.9rem; color: #888;">
                        🍽️ Almuerzo: 
                        <input type="time" name="day_{{ item.employee.day_of_week }}_break_start" value="{{ item.employee.break_start|time:'H:i' }}" class="form-input" style="padding: 5px; width: auto; font-size: 0.8rem;">
                        -
                        <input type="time" name="day_{{ item.employee.day_of_week }}_break_end" value="{{ item.employee.break_end|time:'H:i' }}" class="form-input" style="padding: 5px; width: auto; font-size: 0.8rem;">
                    </div>
                </div>
                {% else %}
                <div style="flex: 1; text-align: center; color: #444; font-style: italic;">
                    Día libre obligatorio.
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>

        <div style="margin-top: 30px; text-align: right;">
            <button type="submit" class="btn btn-primary">Guardar Mi Horario</button>
        </div>
    </form>
</div>
{% endblock %}
"""

# 4.3 Perfil (Instagram + Clave)
profile_html = """{% extends 'base.html' %}
{% block content %}
<div style="padding: 100px 5%; color: white; max-width: 600px; margin: 0 auto;">
    <div style="margin-bottom: 30px;">
        <a href="{% url 'booking:employee_dashboard' %}" style="color: #888; text-decoration: none;">← Volver</a>
        <h1 style="color: #d4af37; margin-top: 10px;">👤 Mi Perfil Profesional</h1>
    </div>

    <form method="post" enctype="multipart/form-data" style="background: #111; padding: 30px; border-radius: 15px; border: 1px solid #333;">
        {% csrf_token %}
        
        <div style="text-align: center; margin-bottom: 30px;">
            <div style="width: 100px; height: 100px; background: #333; border-radius: 50%; margin: 0 auto 10px; display: flex; justify-content: center; align-items: center; overflow: hidden;">
                {% if user.profile_image %}
                    <img src="{{ user.profile_image.url }}" style="width: 100%; height: 100%; object-fit: cover;">
                {% else %}
                    <span style="font-size: 2rem; color: #888;">{{ user.first_name|first }}</span>
                {% endif %}
            </div>
            <label style="color: #d4af37; cursor: pointer; font-size: 0.9rem;">
                Cambiar Foto
                <input type="file" name="profile_image" style="display: none;">
            </label>
        </div>

        {{ form.as_p }}

        <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 20px;">Actualizar Datos</button>
    </form>
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

def main():
    print("👷 CONSTRUYENDO LÓGICA DE EMPLEADO (HORARIO + PERFIL) 👷")
    
    # 1. Forms
    write_file('apps/booking/forms.py', booking_forms)
    
    # 2. Views
    write_file('apps/booking/views.py', booking_views)
    
    # 3. URLs
    write_file('apps/booking/urls.py', booking_urls)
    
    # 4. Templates
    write_file('templates/booking/employee_dashboard.html', dashboard_html)
    write_file('templates/booking/schedule.html', schedule_html)
    write_file('templates/booking/profile.html', profile_html)
    
    print("\n✅ Archivos creados correctamente.")
    print("👉 EJECUTA ESTO EN TU TERMINAL:")
    print("   git add .")
    print('   git commit -m "Feat: Modulo Empleado Completo (Horario + Perfil)"')
    print("   git push origin main")

if __name__ == "__main__":
    main()