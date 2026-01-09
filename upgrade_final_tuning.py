import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. MODELS.PY (AGREGAR DÍAS ACTIVOS AL SALÓN)
# ==========================================
models_content = """
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
    
    # NUEVO: Días que abre el negocio (0=Lunes)
    active_days = models.CharField(max_length=20, default="0,1,2,3,4,5") 
    
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
    work_start = models.TimeField(default='09:00')
    work_end = models.TimeField(default='18:00')
    lunch_start = models.TimeField(default='13:00')
    lunch_end = models.TimeField(default='14:00')
    active_days = models.CharField(max_length=20, default="0,1,2,3,4,5") 
    is_active_today = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Horario de {self.employee.username}"
"""

# ==========================================
# 2. FORMS.PY (DROPDOWNS DE HORAS + DÍAS SALÓN)
# ==========================================
forms_content = """
from django import forms
from .models import Service, Salon, EmployeeSchedule
from apps.core.models import User
from datetime import time

# Generador de opciones de tiempo (cada 30 min)
def get_time_choices():
    choices = []
    for h in range(0, 24):
        for m in (0, 30):
            t = time(h, m)
            label = t.strftime('%I:%M %p')
            val = t.strftime('%H:%M')
            choices.append((val, label))
    return choices

TIME_CHOICES = get_time_choices()

COLOMBIA_CITIES = [
    ('Bogotá D.C.', 'Bogotá D.C.'), ('Medellín', 'Medellín'), ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'), ('Cartagena', 'Cartagena'), ('Bucaramanga', 'Bucaramanga'),
    ('Manizales', 'Manizales'), ('Pereira', 'Pereira'), ('Cúcuta', 'Cúcuta'),
    ('Ibagué', 'Ibagué'), ('Santa Marta', 'Santa Marta'), ('Villavicencio', 'Villavicencio'),
    ('Pasto', 'Pasto'), ('Tunja', 'Tunja'), ('Montería', 'Montería'),
    ('Valledupar', 'Valledupar'), ('Armenia', 'Armenia'), ('Neiva', 'Neiva'),
    ('Popayán', 'Popayán'), ('Sincelejo', 'Sincelejo'), ('Riohacha', 'Riohacha'),
    ('Zipaquirá', 'Zipaquirá'), ('Soacha', 'Soacha'), ('Envigado', 'Envigado'),
    ('Itagüí', 'Itagüí'), ('Bello', 'Bello'), ('Otro', 'Otro (Escribir en dirección)'),
]

class OwnerRegistrationForm(forms.ModelForm):
    salon_name = forms.CharField(label="Nombre del Negocio", required=True)
    salon_address = forms.CharField(label="Dirección del Local", required=True)
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad", required=True)
    phone = forms.CharField(label="WhatsApp (Soporte)", required=True)
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'placeholder': '********'}), required=True)
    password2 = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput(attrs={'placeholder': '********'}), required=True)
    instagram_url = forms.URLField(label="Link Instagram", required=False)
    google_maps_url = forms.URLField(label="Link Google Maps", required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = 'OWNER'
        user.phone = self.cleaned_data["phone"]
        user.city = self.cleaned_data["city"]
        if commit:
            user.save()
            Salon.objects.create(
                owner=user,
                name=self.cleaned_data["salon_name"],
                address=self.cleaned_data["salon_address"],
                city=self.cleaned_data["city"],
                instagram_url=self.cleaned_data.get("instagram_url", ""),
                google_maps_url=self.cleaned_data.get("google_maps_url", ""),
                opening_time="08:00",
                closing_time="20:00"
            )
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-black focus:border-black sm:text-sm'

class OwnerUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

class SalonUpdateForm(forms.ModelForm):
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad Base")
    class Meta:
        model = Salon
        fields = ['name', 'address', 'city', 'instagram_url', 'google_maps_url']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'duration_minutes', 'price', 'buffer_time']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

class EmployeeCreationForm(forms.ModelForm):
    username = forms.CharField(label="Usuario de Acceso", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña", required=True)
    first_name = forms.CharField(label="Nombre", required=True)
    last_name = forms.CharField(label="Apellido", required=True)
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'phone']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- NUEVO: HORARIO DE APERTURA DEL SALÓN CON DÍAS Y DROPDOWNS ---
class SalonScheduleForm(forms.ModelForm):
    opening_time = forms.ChoiceField(choices=TIME_CHOICES, label="Apertura")
    closing_time = forms.ChoiceField(choices=TIME_CHOICES, label="Cierre")
    
    # Días que abre el negocio
    DAYS_CHOICES = [
        ('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miércoles'), 
        ('3', 'Jueves'), ('4', 'Viernes'), ('5', 'Sábado'), ('6', 'Domingo')
    ]
    active_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES, 
        widget=forms.CheckboxSelectMultiple,
        label="Días de Apertura"
    )

    class Meta:
        model = Salon
        fields = ['opening_time', 'closing_time', 'active_days', 'deposit_percentage']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.active_days:
            self.initial['active_days'] = self.instance.active_days.split(',')
        
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

    def clean_active_days(self):
        days = self.cleaned_data['active_days']
        return ','.join(days)

# --- NUEVO: HORARIO EMPLEADO CON DROPDOWNS ---
class EmployeeScheduleUpdateForm(forms.ModelForm):
    work_start = forms.ChoiceField(choices=TIME_CHOICES, label="Inicio de Turno")
    work_end = forms.ChoiceField(choices=TIME_CHOICES, label="Fin de Turno")
    lunch_start = forms.ChoiceField(choices=TIME_CHOICES, label="Inicio Almuerzo")
    lunch_end = forms.ChoiceField(choices=TIME_CHOICES, label="Fin Almuerzo")
    
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
        if self.instance and self.instance.pk and self.instance.active_days:
            self.initial['active_days'] = self.instance.active_days.split(',')
            
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

    def clean_active_days(self):
        days = self.cleaned_data['active_days']
        return ','.join(days)
"""

# ==========================================
# 3. LOGIC.PY (CEREBRO: VALIDAR DÍAS SALÓN)
# ==========================================
logic_content = """
from datetime import datetime, timedelta, time, date
from django.utils import timezone

class AvailabilityManager:
    @staticmethod
    def is_salon_open(salon, check_time=None):
        if not check_time:
            check_time = timezone.localtime(timezone.now()).time()
        
        # 1. Validar Día de la Semana
        today_idx = str(timezone.localtime(timezone.now()).weekday())
        if hasattr(salon, 'active_days') and salon.active_days:
            if today_idx not in salon.active_days.split(','):
                return False

        # 2. Validar Hora
        open_t = salon.opening_time
        close_t = salon.closing_time
        
        if open_t == close_t: return False
        if open_t < close_t:
            return open_t <= check_time <= close_t
        else:
            return check_time >= open_t or check_time <= close_t

    @staticmethod
    def get_available_slots(salon, service, employee, target_date):
        slots = []
        day_of_week = str(target_date.weekday())

        # 1. FILTRO SUPREMO: ¿El Negocio abre hoy?
        if hasattr(salon, 'active_days') and salon.active_days:
            if day_of_week not in salon.active_days.split(','):
                return [] # Negocio cerrado hoy

        # 2. ¿El Empleado trabaja hoy?
        try:
            schedule = employee.schedule
            if day_of_week not in schedule.active_days.split(','):
                return [] # Empleado descansa hoy
        except:
            return []

        # 3. Definir ventana de tiempo (Intersección)
        start_hour = max(salon.opening_time, schedule.work_start)
        end_hour = min(salon.closing_time, schedule.work_end)
        
        if start_hour >= end_hour:
            return []

        current_dt = datetime.combine(target_date, start_hour)
        end_dt = datetime.combine(target_date, end_hour)
        lunch_start_dt = datetime.combine(target_date, schedule.lunch_start)
        lunch_end_dt = datetime.combine(target_date, schedule.lunch_end)
        duration = timedelta(minutes=service.duration_minutes + service.buffer_time)

        while current_dt + duration <= end_dt:
            slot_end = current_dt + duration
            is_valid = True
            
            if (slot_end > lunch_start_dt) and (current_dt < lunch_end_dt):
                is_valid = False
            
            # Aquí se conectará la validación de citas existentes (Appointment)
            
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
# 4. REAPER COMMAND (LIBERAR CITAS VENCIDAS)
# ==========================================
reaper_content = """
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import User
from apps.marketplace.models import Appointment
from datetime import timedelta

class Command(BaseCommand):
    help = 'El Reaper: Elimina cuentas no pagadas > 24h y citas pendientes > 60min'

    def handle(self, *args, **kwargs):
        # 1. Eliminar Dueños Morosos
        limit_time_owners = timezone.now() - timedelta(hours=24)
        expired_owners = User.objects.filter(role='OWNER', is_verified_payment=False, registration_timestamp__lt=limit_time_owners)
        owners_count = expired_owners.count()
        expired_owners.delete()
        
        # 2. ELIMINAR CITAS PENDIENTES (> 60 MIN) - ¡AQUÍ ESTÁ LA MAGIA!
        limit_time_apps = timezone.now() - timedelta(minutes=60)
        expired_apps = Appointment.objects.filter(status='PENDING', created_at__lt=limit_time_apps)
        apps_count = expired_apps.count()
        expired_apps.delete()
        
        self.stdout.write(self.style.SUCCESS(f'Reaper Reporte: {owners_count} dueños eliminados, {apps_count} citas liberadas.'))
"""

# ==========================================
# 5. ACTUALIZAR SETTINGS.HTML (PARA MOSTRAR CHECKBOXES)
# ==========================================
# Actualizamos el template de settings para renderizar bien los checkboxes del salon
html_settings = """
{% extends 'base.html' %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-8 border-b pb-4">
        <div>
            <h1 class="text-3xl font-serif font-bold text-gray-900">Configuración</h1>
            <p class="text-gray-500 text-sm">Gestiona tu identidad y tus reglas.</p>
        </div>
        <a href="{% url 'dashboard' %}" class="text-sm font-bold text-gray-600 hover:text-black">&larr; Volver</a>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-10">
        <div>
            <div class="bg-white p-8 rounded-xl shadow border border-gray-100 mb-8">
                <h2 class="text-xl font-bold mb-6 flex items-center">
                    <span class="bg-black text-white w-8 h-8 rounded-full flex items-center justify-center mr-3 text-sm">1</span>
                    Identidad
                </h2>
                <form method="post">
                    {% csrf_token %}
                    <h3 class="text-xs font-bold text-gray-400 uppercase mb-4">Dueño</h3>
                    <div class="grid grid-cols-2 gap-4 mb-4">
                        <div><label class="block text-xs font-medium text-gray-700 mb-1">Nombre</label>{{ owner_form.first_name }}</div>
                        <div><label class="block text-xs font-medium text-gray-700 mb-1">Apellido</label>{{ owner_form.last_name }}</div>
                    </div>
                    <div class="mb-4"><label class="block text-xs font-medium text-gray-700 mb-1">WhatsApp</label>{{ owner_form.phone }}</div>
                    <div class="mb-6"><label class="block text-xs font-medium text-gray-700 mb-1">Email</label>{{ owner_form.email }}</div>
                    <hr class="border-gray-100 my-6">
                    <h3 class="text-xs font-bold text-gray-400 uppercase mb-4">Negocio</h3>
                    <div class="mb-4"><label class="block text-xs font-medium text-gray-700 mb-1">Nombre</label>{{ salon_form.name }}</div>
                    <div class="mb-4"><label class="block text-xs font-medium text-gray-700 mb-1">Ciudad</label>{{ salon_form.city }}</div>
                    <div class="mb-4"><label class="block text-xs font-medium text-gray-700 mb-1">Dirección</label>{{ salon_form.address }}</div>
                    <div class="grid grid-cols-2 gap-4 mb-6">
                        <div><label class="block text-xs font-medium text-gray-700 mb-1">Instagram</label>{{ salon_form.instagram_url }}</div>
                        <div><label class="block text-xs font-medium text-gray-700 mb-1">Maps</label>{{ salon_form.google_maps_url }}</div>
                    </div>
                    <button type="submit" name="update_profile" class="w-full bg-gray-900 text-white py-3 rounded-lg font-bold hover:bg-black transition shadow-lg">Guardar Identidad</button>
                </form>
            </div>
        </div>

        <div>
            <div class="bg-white p-8 rounded-xl shadow border border-gray-100">
                <h2 class="text-xl font-bold mb-6 flex items-center">
                    <span class="bg-black text-white w-8 h-8 rounded-full flex items-center justify-center mr-3 text-sm">2</span>
                    Reglas de Operación
                </h2>
                <form method="post">
                    {% csrf_token %}
                    <div class="grid grid-cols-2 gap-6 mb-6">
                        <div><label class="block text-xs font-medium text-gray-700 mb-2">Apertura</label>{{ schedule_form.opening_time }}</div>
                        <div><label class="block text-xs font-medium text-gray-700 mb-2">Cierre</label>{{ schedule_form.closing_time }}</div>
                    </div>
                    
                    <div class="mb-6">
                        <label class="text-xs font-bold text-gray-400 uppercase block mb-2">Días de Servicio</label>
                        <div class="grid grid-cols-2 gap-2 text-sm">
                            {% for checkbox in schedule_form.active_days %}
                            <label class="flex items-center space-x-2 cursor-pointer">
                                {{ checkbox.tag }}
                                <span>{{ checkbox.choice_label }}</span>
                            </label>
                            {% endfor %}
                        </div>
                    </div>

                    <hr class="border-gray-100 my-6">
                    <div class="mb-6">
                        <label class="block text-xs font-medium text-gray-700 mb-2">Porcentaje de Abono (%)</label>
                        {{ schedule_form.deposit_percentage }}
                    </div>
                    <button type="submit" name="update_schedule" class="w-full bg-white text-black border-2 border-black py-3 rounded-lg font-bold hover:bg-gray-50 transition">Actualizar Reglas</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 6. EJECUCIÓN
# ==========================================
def run_tuning():
    print("🎻 AFINANDO EL INSTRUMENTO...")

    # 1. Models (Nuevo campo Salon)
    with open(BASE_DIR / 'apps' / 'businesses' / 'models.py', 'w', encoding='utf-8') as f:
        f.write(models_content.strip())
    print("✅ Models: Campo active_days agregado al Salón.")

    # 2. Forms (Dropdowns y Checkboxes)
    with open(BASE_DIR / 'apps' / 'businesses' / 'forms.py', 'w', encoding='utf-8') as f:
        f.write(forms_content.strip())
    print("✅ Forms: Inputs de hora cambiados a Select.")

    # 3. Logic (Filtro Supremo)
    with open(BASE_DIR / 'apps' / 'businesses' / 'logic.py', 'w', encoding='utf-8') as f:
        f.write(logic_content.strip())
    print("✅ Logic: El Cerebro ahora respeta los días del negocio.")

    # 4. Reaper (Liberador de citas)
    reaper_path = BASE_DIR / 'apps' / 'core' / 'management' / 'commands' / 'run_reaper.py'
    with open(reaper_path, 'w', encoding='utf-8') as f:
        f.write(reaper_content.strip())
    print("✅ Reaper: Activada la limpieza de citas pendientes.")

    # 5. Template Settings
    with open(BASE_DIR / 'templates' / 'businesses' / 'settings.html', 'w', encoding='utf-8') as f:
        f.write(html_settings.strip())
    print("✅ Template: Configuración actualizada.")

if __name__ == "__main__":
    run_tuning()
    print("\n⚠️ IMPORTANTE: Hubo cambios en modelos. Debes:")
    print("1. python manage.py makemigrations businesses")
    print("2. git add .")
    print("3. git commit")
    print("4. git push")