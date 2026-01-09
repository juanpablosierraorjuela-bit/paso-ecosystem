import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. ACTUALIZAR MODELS.PY (Horarios Empleado)
# ==========================================
models_businesses_content = """
from django.db import models
from django.conf import settings

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_salon')
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    
    deposit_percentage = models.IntegerField(default=50)
    instagram_url = models.URLField(blank=True)
    google_maps_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    duration_minutes = models.IntegerField(help_text="Duración en minutos")
    buffer_time = models.IntegerField(default=15, help_text="Limpieza (min)")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} - {self.salon.name}"

class EmployeeSchedule(models.Model):
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedule')
    
    # Configuración de Turno
    work_start = models.TimeField(default='09:00')
    work_end = models.TimeField(default='18:00')
    
    # Configuración de Almuerzo
    lunch_start = models.TimeField(default='13:00')
    lunch_end = models.TimeField(default='14:00')
    
    # Días Activos (Guardados como string "0,1,2,3,4" donde 0=Lunes)
    active_days = models.CharField(max_length=20, default="0,1,2,3,4,5") 
    
    is_active_today = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Horario de {self.employee.username}"
"""

# ==========================================
# 2. ACTUALIZAR FORMS.PY (Formulario Empleado)
# ==========================================
# Agregamos EmployeeScheduleForm al final del archivo existente
forms_append = """

# --- HORARIO DEL EMPLEADO ---
class EmployeeScheduleUpdateForm(forms.ModelForm):
    work_start = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Inicio de Turno")
    work_end = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Fin de Turno")
    lunch_start = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Inicio Almuerzo")
    lunch_end = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Fin Almuerzo")
    
    # Días laborales (Checkboxes)
    DAYS_CHOICES = [
        ('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miércoles'), 
        ('3', 'Jueves'), ('4', 'Viernes'), ('5', 'Sábado'), ('6', 'Domingo')
    ]
    active_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES, 
        widget=forms.CheckboxSelectMultiple,
        label="Días Laborales"
    )

    class Meta:
        model = EmployeeSchedule
        fields = ['work_start', 'work_end', 'lunch_start', 'lunch_end', 'active_days']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Parsear string a lista para los checkboxes si hay datos
        if self.instance and self.instance.pk and self.instance.active_days:
            self.initial['active_days'] = self.instance.active_days.split(',')

    def clean_active_days(self):
        days = self.cleaned_data['active_days']
        return ','.join(days)
"""

# ==========================================
# 3. ACTUALIZAR LOGIC.PY (EL ALGORITMO DIOS)
# ==========================================
logic_content = """
from datetime import datetime, timedelta, time, date
from django.utils import timezone

class AvailabilityManager:
    @staticmethod
    def is_salon_open(salon, check_time=None):
        if not check_time:
            check_time = timezone.localtime(timezone.now()).time()
        
        open_t = salon.opening_time
        close_t = salon.closing_time
        
        if open_t == close_t: return False
        if open_t < close_t:
            return open_t <= check_time <= close_t
        else:
            return check_time >= open_t or check_time <= close_t

    @staticmethod
    def get_available_slots(salon, service, employee, target_date):
        \"\"\"
        ALGORITMO MAESTRO DE DISPONIBILIDAD
        Cruza: Horario Negocio + Horario Empleado + Almuerzo + Duración Servicio
        \"\"\"
        slots = []
        
        # 1. Verificar si el empleado trabaja ese día de la semana
        # 0=Lunes, 6=Domingo
        day_of_week = str(target_date.weekday())
        try:
            schedule = employee.schedule
            if day_of_week not in schedule.active_days.split(','):
                return [] # No trabaja hoy
        except:
            return [] # No tiene horario configurado

        # 2. Definir ventana de tiempo (Intersección Negocio vs Empleado)
        # El inicio es el MÁXIMO entre (Apertura Negocio, Entrada Empleado)
        start_hour = max(salon.opening_time, schedule.work_start)
        
        # El fin es el MÍNIMO entre (Cierre Negocio, Salida Empleado)
        # Nota simplificada: Asumimos por ahora que no hay turno nocturno cruzado para empleados
        # para no complicar la Fase 3, pero el sistema lo soporta si se ajusta.
        end_hour = min(salon.closing_time, schedule.work_end)
        
        if start_hour >= end_hour:
            return [] # Horarios incompatibles

        # Convertir a datetime para sumar minutos
        current_dt = datetime.combine(target_date, start_hour)
        end_dt = datetime.combine(target_date, end_hour)
        
        # Almuerzo
        lunch_start_dt = datetime.combine(target_date, schedule.lunch_start)
        lunch_end_dt = datetime.combine(target_date, schedule.lunch_end)

        # Duración total requerida (Servicio + Limpieza)
        duration = timedelta(minutes=service.duration_minutes + service.buffer_time)

        # 3. Iterar cada 30 min buscando huecos
        while current_dt + duration <= end_dt:
            slot_end = current_dt + duration
            is_valid = True
            
            # A. Validar Almuerzo (Si la cita choca con la hora de comida)
            # Choca si el fin de la cita es después del inicio del almuerzo 
            # Y el inicio de la cita es antes del fin del almuerzo
            if (slot_end > lunch_start_dt) and (current_dt < lunch_end_dt):
                is_valid = False
            
            # B. Validar Citas Existentes (Base de Datos)
            # (Aquí iría la consulta a Appointment.objects.filter(...) en Fase 4)
            
            # C. Agregar si es válido
            if is_valid:
                slots.append({
                    'time_obj': current_dt.time(),
                    'label': current_dt.strftime("%I:%M %p"),
                    'is_available': True 
                })
            
            current_dt += timedelta(minutes=30)
            
        return slots
"""

# ==========================================
# 4. VIEWS.PY (DASHBOARD EMPLEADO)
# ==========================================
# Agregaremos la vista 'employee_dashboard' al archivo existente
# Para eso leemos y adjuntamos.

def update_views():
    views_path = BASE_DIR / 'apps' / 'businesses' / 'views.py'
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Importar el nuevo form y modelo
    if "EmployeeScheduleUpdateForm" not in content:
        content = content.replace(
            "from .forms import ServiceForm, EmployeeCreationForm, SalonScheduleForm, OwnerUpdateForm, SalonUpdateForm",
            "from .forms import ServiceForm, EmployeeCreationForm, SalonScheduleForm, OwnerUpdateForm, SalonUpdateForm, EmployeeScheduleUpdateForm"
        )
        content = content.replace(
            "from .models import Service, Salon",
            "from .models import Service, Salon, EmployeeSchedule"
        )

    # Vista del Dashboard Empleado
    employee_view = """

# --- PANEL DEL EMPLEADO (MI AGENDA) ---
@login_required
def employee_dashboard(request):
    if request.user.role != 'EMPLOYEE':
        return redirect('dashboard') # Si es dueño, a su panel
    
    # Asegurar que tenga un horario creado
    schedule, created = EmployeeSchedule.objects.get_or_create(employee=request.user)
    
    if request.method == 'POST':
        form = EmployeeScheduleUpdateForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu disponibilidad ha sido actualizada.")
            return redirect('employee_dashboard')
    else:
        form = EmployeeScheduleUpdateForm(instance=schedule)
    
    return render(request, 'businesses/employee_dashboard.html', {
        'form': form,
        'schedule': schedule,
        'salon': request.user.workplace
    })
"""
    if "def employee_dashboard" not in content:
        content += employee_view
        
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)

# ==========================================
# 5. URLS.PY (MAPEAR LA RUTA BIBLICA)
# ==========================================
def update_urls():
    urls_path = BASE_DIR / 'apps' / 'businesses' / 'urls.py'
    with open(urls_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "name='employee_dashboard'" not in content:
        # Agregamos la ruta mi-agenda
        new_pattern = "    path('mi-agenda/', views.employee_dashboard, name='employee_dashboard'),"
        content = content.replace(
            "urlpatterns = [",
            f"urlpatterns = [\n{new_pattern}"
        )
        
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(content)

# ==========================================
# 6. TEMPLATE (PANEL EMPLEADO)
# ==========================================
html_employee_dash = """
{% extends 'base.html' %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    
    <div class="flex justify-between items-center mb-8 border-b pb-4">
        <div>
            <h1 class="text-3xl font-serif font-bold text-gray-900">Hola, {{ user.first_name }}</h1>
            <p class="text-gray-500">Talento en <strong>{{ salon.name }}</strong></p>
        </div>
        <div class="text-right">
            <span class="bg-black text-white text-xs font-bold px-3 py-1 rounded-full">
                PANEL EMPLEADO
            </span>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <div class="lg:col-span-1">
            <div class="bg-white p-6 rounded-xl shadow border border-gray-100">
                <h2 class="text-xl font-bold mb-4 flex items-center">
                    ⏰ Mi Disponibilidad
                </h2>
                <p class="text-sm text-gray-500 mb-6">Define cuándo puedes recibir clientes. El sistema bloqueará automáticamente tu hora de almuerzo.</p>
                
                <form method="post">
                    {% csrf_token %}
                    
                    <div class="bg-gray-50 p-3 rounded-lg mb-4">
                        <label class="text-xs font-bold text-gray-400 uppercase">Jornada Laboral</label>
                        <div class="grid grid-cols-2 gap-2 mt-2">
                            <div>
                                <span class="text-xs text-gray-600">Entrada</span>
                                {{ form.work_start }}
                            </div>
                            <div>
                                <span class="text-xs text-gray-600">Salida</span>
                                {{ form.work_end }}
                            </div>
                        </div>
                    </div>

                    <div class="bg-gray-50 p-3 rounded-lg mb-4">
                        <label class="text-xs font-bold text-gray-400 uppercase">Hora de Almuerzo</label>
                        <div class="grid grid-cols-2 gap-2 mt-2">
                            <div>
                                <span class="text-xs text-gray-600">Inicio</span>
                                {{ form.lunch_start }}
                            </div>
                            <div>
                                <span class="text-xs text-gray-600">Fin</span>
                                {{ form.lunch_end }}
                            </div>
                        </div>
                    </div>

                    <div class="mb-6">
                        <label class="text-xs font-bold text-gray-400 uppercase block mb-2">Días Activos</label>
                        <div class="grid grid-cols-2 gap-2 text-sm">
                            {% for checkbox in form.active_days %}
                            <label class="flex items-center space-x-2 cursor-pointer">
                                {{ checkbox.tag }}
                                <span>{{ checkbox.choice_label }}</span>
                            </label>
                            {% endfor %}
                        </div>
                    </div>

                    <button type="submit" class="w-full bg-black text-white py-3 rounded-lg font-bold hover:bg-gray-800 transition">
                        Actualizar Mi Horario
                    </button>
                </form>
            </div>
        </div>

        <div class="lg:col-span-2">
            <div class="bg-white p-6 rounded-xl shadow border border-gray-100 min-h-[400px]">
                <h2 class="text-xl font-bold mb-6">📅 Mis Citas Confirmadas</h2>
                
                <div class="text-center py-12 bg-gray-50 rounded-xl border-dashed border-2 border-gray-200">
                    <div class="text-4xl mb-3">📭</div>
                    <p class="text-gray-500 font-medium">No tienes citas verificadas para hoy.</p>
                    <p class="text-xs text-gray-400 mt-2">Las citas aparecerán aquí cuando el dueño confirme el pago.</p>
                </div>
            </div>
        </div>

    </div>
</div>

<style>
    /* Estilo simple para los inputs de hora */
    input[type="time"] {
        width: 100%;
        padding: 4px;
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        font-family: monospace;
    }
</style>
{% endblock %}
"""

# ==========================================
# 7. EJECUCIÓN
# ==========================================
def apply_brain():
    print("🧠 CONSTRUYENDO CEREBRO Y PANEL DE EMPLEADO...")

    # 1. Models
    with open(BASE_DIR / 'apps' / 'businesses' / 'models.py', 'w', encoding='utf-8') as f:
        f.write(models_businesses_content.strip())
    print("✅ apps/businesses/models.py: Modelo de Horario actualizado.")

    # 2. Forms (Append)
    with open(BASE_DIR / 'apps' / 'businesses' / 'forms.py', 'a', encoding='utf-8') as f:
        f.write(forms_append)
    print("✅ apps/businesses/forms.py: Formulario de horario agregado.")

    # 3. Logic
    with open(BASE_DIR / 'apps' / 'businesses' / 'logic.py', 'w', encoding='utf-8') as f:
        f.write(logic_content.strip())
    print("✅ apps/businesses/logic.py: Algoritmo de intersección horaria listo.")

    # 4. Views & URLs
    update_views()
    update_urls()
    print("✅ Views y URLs configuradas.")

    # 5. Template
    with open(BASE_DIR / 'templates' / 'businesses' / 'employee_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_employee_dash.strip())
    print("✅ templates/businesses/employee_dashboard.html creado.")

if __name__ == "__main__":
    apply_brain()
    print("\n⚠️ IMPORTANTE: Como cambiamos los modelos, debes crear migraciones.")
    print("1. Ejecuta: python manage.py makemigrations")
    print("2. Ejecuta: python manage.py migrate")
    print("3. Luego sube a GitHub.")