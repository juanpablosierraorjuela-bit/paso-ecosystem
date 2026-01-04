import os
import subprocess

# -----------------------------------------------------------------------------
# 1. ASEGURAR FORMS.PY (Con lista de ciudades y Meta corregido)
# -----------------------------------------------------------------------------
forms_path = os.path.join('apps', 'businesses', 'forms.py')
print(f" Actualizando formulario en {forms_path}...")

new_forms_code = r"""from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee, EmployeeSchedule
from datetime import datetime

User = get_user_model()

# --- LISTA DE CIUDADES DE COLOMBIA ---
COLOMBIA_CITIES = [
    ('Bogotá', 'Bogotá'), ('Medellín', 'Medellín'), ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'), ('Cartagena', 'Cartagena'), ('Cúcuta', 'Cúcuta'),
    ('Bucaramanga', 'Bucaramanga'), ('Pereira', 'Pereira'), ('Santa Marta', 'Santa Marta'),
    ('Ibagué', 'Ibagué'), ('Pasto', 'Pasto'), ('Manizales', 'Manizales'),
    ('Neiva', 'Neiva'), ('Villavicencio', 'Villavicencio'), ('Armenia', 'Armenia'),
    ('Valledupar', 'Valledupar'), ('Montería', 'Montería'), ('Sincelejo', 'Sincelejo'),
    ('Popayán', 'Popayán'), ('Tunja', 'Tunja'), ('Riohacha', 'Riohacha'),
    ('Florencia', 'Florencia'), ('Quibdó', 'Quibdó'), ('Arauca', 'Arauca'),
    ('Yopal', 'Yopal'), ('Leticia', 'Leticia'), ('San Andrés', 'San Andrés'),
    ('Mocoa', 'Mocoa'), ('Mitú', 'Mitú'), ('Puerto Carreño', 'Puerto Carreño'),
    ('Inírida', 'Inírida'), ('San José del Guaviare', 'San José del Guaviare'),
    ('Sogamoso', 'Sogamoso'), ('Duitama', 'Duitama'), ('Girardot', 'Girardot'),
    ('Barrancabermeja', 'Barrancabermeja'), ('Buenaventura', 'Buenaventura'),
    ('Tumaco', 'Tumaco'), ('Ipiales', 'Ipiales'), ('Palmira', 'Palmira'),
    ('Tuluá', 'Tuluá'), ('Buga', 'Buga'), ('Cartago', 'Cartago'),
    ('Soacha', 'Soacha'), ('Bello', 'Bello'), ('Itagüí', 'Itagüí'),
    ('Envigado', 'Envigado'), ('Apartadó', 'Apartadó'),
]

# Generador de horas
TIME_CHOICES = []
for h in range(5, 23):
    for m in (0, 30):
        time_str = f"{h:02d}:{m:02d}"
        display_str = datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
        TIME_CHOICES.append((time_str, display_str))

class EmployeeScheduleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        if self.instance.pk:
            for day in days:
                db_val = getattr(self.instance, f"{day}_hours", "CERRADO")
                is_active = db_val != "CERRADO"
                self.fields[f"{day}_active"].initial = is_active
                if is_active and '-' in db_val:
                    start, end = db_val.split('-')
                    self.fields[f"{day}_start"].initial = start
                    self.fields[f"{day}_end"].initial = end

        if self.salon:
            map_salon = {
                'monday': self.salon.work_monday, 'tuesday': self.salon.work_tuesday,
                'wednesday': self.salon.work_wednesday, 'thursday': self.salon.work_thursday,
                'friday': self.salon.work_friday, 'saturday': self.salon.work_saturday,
                'sunday': self.salon.work_sunday
            }
            for day, works in map_salon.items():
                if not works:
                    self.fields[f"{day}_active"].disabled = True
                    self.fields[f"{day}_active"].help_text = "Cerrado por el negocio."
                    self.fields[f"{day}_active"].initial = False

    monday_active = forms.BooleanField(required=False, label="Lunes")
    monday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    monday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    tuesday_active = forms.BooleanField(required=False, label="Martes")
    tuesday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    tuesday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    wednesday_active = forms.BooleanField(required=False, label="Miércoles")
    wednesday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    wednesday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    thursday_active = forms.BooleanField(required=False, label="Jueves")
    thursday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    thursday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    friday_active = forms.BooleanField(required=False, label="Viernes")
    friday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    friday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    saturday_active = forms.BooleanField(required=False, label="Sábado")
    saturday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    saturday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    sunday_active = forms.BooleanField(required=False, label="Domingo")
    sunday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    sunday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)

    class Meta:
        model = EmployeeSchedule
        fields = []

    def save(self, commit=True):
        schedule = super().save(commit=False)
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            is_active = self.cleaned_data.get(f"{day}_active")
            start = self.cleaned_data.get(f"{day}_start")
            end = self.cleaned_data.get(f"{day}_end")
            if is_active and start and end:
                setattr(schedule, f"{day}_hours", f"{start}-{end}")
            else:
                setattr(schedule, f"{day}_hours", "CERRADO")
        if commit: schedule.save()
        return schedule

class SalonRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Usuario", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: tu_negocio_2026'}))
    email = forms.EmailField(label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'}), label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'}), label="Confirmar Contraseña")
    
    salon_name = forms.CharField(max_length=255, label="Nombre del Negocio", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Barbería Estilo'}))
    
    # LISTA DESPLEGABLE DE CIUDADES
    city = forms.ChoiceField(
        choices=COLOMBIA_CITIES, 
        label="Ciudad", 
        initial='Bogotá',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    address = forms.CharField(max_length=255, label="Dirección", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle 123 # 45-67'}))
    phone = forms.CharField(max_length=50, label="Teléfono/WhatsApp", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '300 123 4567'}))
    instagram_link = forms.URLField(required=False, label="Instagram (Opcional)", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/tu_negocio'}))
    maps_link = forms.URLField(required=False, label="Google Maps (Opcional)", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://maps.google.com/...'}))

    class Meta:
        model = User
        fields = ['username', 'email'] # Solo campos del modelo User

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2: raise forms.ValidationError("Las contraseñas no coinciden")
        return p2

class SalonSettingsForm(forms.ModelForm):
    city = forms.ChoiceField(
        choices=COLOMBIA_CITIES, 
        label="Ciudad",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = Salon
        fields = ['name', 'city', 'address', 'whatsapp_number', 'instagram_link', 'maps_link', 
                  'opening_time', 'closing_time', 'deposit_percentage',
                  'work_monday', 'work_tuesday', 'work_wednesday', 'work_thursday', 'work_friday', 'work_saturday', 'work_sunday']
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-control'}),
            'maps_link': forms.URLInput(attrs={'class': 'form-control'}),
            'deposit_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'price', 'buffer_time', 'is_active']

class EmployeeForm(forms.ModelForm):
    username = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    class Meta:
        model = Employee
        fields = ['name', 'phone', 'instagram_link', 'is_active']
"""
with open(forms_path, 'w', encoding='utf-8') as f:
    f.write(new_forms_code)


# -----------------------------------------------------------------------------
# 2. RECONSTRUIR REGISTER_OWNER.HTML (Para mostrar el Desplegable y Errores)
# -----------------------------------------------------------------------------
template_path = os.path.join('templates', 'registration', 'register_owner.html')
print(f" Reconstruyendo plantilla en {template_path}...")

new_template_code = r"""{% extends 'master.html' %}
{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
            <div class="card border-0 shadow-lg rounded-4 overflow-hidden">
                <div class="card-header bg-dark text-white p-4 text-center">
                    <h3 class="mb-0 fw-bold">Registro de Negocio</h3>
                    <p class="mb-0 text-white-50">Únete a Paso Ecosystem</p>
                </div>
                <div class="card-body p-5 bg-light">
                    
                    {% if form.non_field_errors %}
                        <div class="alert alert-danger rounded-3 border-0 shadow-sm mb-4">
                            {% for error in form.non_field_errors %}
                                <div class="d-flex align-items-center">
                                    <i class="fas fa-exclamation-circle me-2"></i>
                                    {{ error }}
                                </div>
                            {% endfor %}
                        </div>
                    {% endif %}

                    <form method="post">
                        {% csrf_token %}
                        
                        <h5 class="fw-bold mb-3 text-secondary">Datos de Acceso</h5>
                        
                        <div class="mb-3">
                            <label class="form-label fw-bold small">Usuario</label>
                            {{ form.username }}
                            {% if form.username.errors %}
                                <div class="text-danger small mt-1">{{ form.username.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <div class="mb-3">
                            <label class="form-label fw-bold small">Correo Electrónico</label>
                            {{ form.email }}
                            {% if form.email.errors %}
                                <div class="text-danger small mt-1">{{ form.email.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <div class="row g-2 mb-4">
                            <div class="col-6">
                                <label class="form-label fw-bold small">Contraseña</label>
                                {{ form.password1 }}
                                {% if form.password1.errors %}
                                    <div class="text-danger small mt-1">{{ form.password1.errors.0 }}</div>
                                {% endif %}
                            </div>
                            <div class="col-6">
                                <label class="form-label fw-bold small">Confirmar</label>
                                {{ form.password2 }}
                                {% if form.password2.errors %}
                                    <div class="text-danger small mt-1">{{ form.password2.errors.0 }}</div>
                                {% endif %}
                            </div>
                        </div>

                        <hr class="my-4 text-muted">
                        <h5 class="fw-bold mb-3 text-secondary">Información del Negocio</h5>

                        <div class="mb-3">
                            <label class="form-label fw-bold small">Nombre del Negocio</label>
                            {{ form.salon_name }}
                            {% if form.salon_name.errors %}
                                <div class="text-danger small mt-1">{{ form.salon_name.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <div class="mb-3">
                            <label class="form-label fw-bold small">Ciudad</label>
                            {{ form.city }}
                            {% if form.city.errors %}
                                <div class="text-danger small mt-1">{{ form.city.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <div class="mb-3">
                            <label class="form-label fw-bold small">Dirección Física</label>
                            {{ form.address }}
                            {% if form.address.errors %}
                                <div class="text-danger small mt-1">{{ form.address.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <div class="mb-3">
                            <label class="form-label fw-bold small">Teléfono / WhatsApp</label>
                            {{ form.phone }}
                            {% if form.phone.errors %}
                                <div class="text-danger small mt-1">{{ form.phone.errors.0 }}</div>
                            {% endif %}
                        </div>

                        <div class="row g-2 mb-4">
                            <div class="col-12">
                                <label class="form-label fw-bold small text-muted">Instagram (Opcional)</label>
                                {{ form.instagram_link }}
                            </div>
                            <div class="col-12">
                                <label class="form-label fw-bold small text-muted">Google Maps (Opcional)</label>
                                {{ form.maps_link }}
                            </div>
                        </div>

                        <div class="d-grid gap-2 mt-5">
                            <button type="submit" class="btn btn-dark btn-lg rounded-pill fw-bold shadow hover-scale">
                                Registrar Negocio <i class="fas fa-arrow-right ms-2"></i>
                            </button>
                            <a href="{% url 'home' %}" class="btn btn-link text-muted text-decoration-none">Cancelar</a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(new_template_code)

# -----------------------------------------------------------------------------
# 3. SUBIR A GITHUB
# -----------------------------------------------------------------------------
print(" Subiendo arreglos de registro a GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix: Formulario registro con Desplegable Ciudades y Errores visibles"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print(" ¡LISTO! Formulario de registro reparado.")
except Exception as e:
    print(f" Error Git: {e}")

try:
    os.remove(__file__)
except:
    pass