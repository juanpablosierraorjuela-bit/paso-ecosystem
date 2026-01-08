import os

# ==========================================
# 1. ACTUALIZAR FORMS.PY CON CIUDADES DE COLOMBIA
# ==========================================

forms_content = """from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee, EmployeeSchedule
from datetime import datetime

User = get_user_model()

# Lista de Ciudades de Colombia
COLOMBIA_CITIES = [
    ('Bogotá', 'Bogotá D.C.'),
    ('Medellín', 'Medellín'),
    ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'),
    ('Cartagena', 'Cartagena'),
    ('Bucaramanga', 'Bucaramanga'),
    ('Manizales', 'Manizales'),
    ('Pereira', 'Pereira'),
    ('Cúcuta', 'Cúcuta'),
    ('Ibagué', 'Ibagué'),
    ('Santa Marta', 'Santa Marta'),
    ('Villavicencio', 'Villavicencio'),
    ('Pasto', 'Pasto'),
    ('Montería', 'Montería'),
    ('Valledupar', 'Valledupar'),
    ('Neiva', 'Neiva'),
    ('Armenia', 'Armenia'),
    ('Popayán', 'Popayán'),
    ('Sincelejo', 'Sincelejo'),
    ('Riohacha', 'Riohacha'),
    ('Tunja', 'Tunja'),
    ('Florencia', 'Florencia'),
    ('Yopal', 'Yopal'),
    ('Quibdó', 'Quibdó'),
    ('San Andrés', 'San Andrés'),
    ('Leticia', 'Leticia'),
    ('Arauca', 'Arauca'),
    ('Mocoa', 'Mocoa'),
    ('San José del Guaviare', 'San José del Guaviare'),
    ('Mitú', 'Mitú'),
    ('Puerto Carreño', 'Puerto Carreño'),
    ('Inírida', 'Inírida'),
    ('Soacha', 'Soacha'),
    ('Bello', 'Bello'),
    ('Itagüí', 'Itagüí'),
    ('Envigado', 'Envigado'),
    ('Palmira', 'Palmira'),
    ('Buenaventura', 'Buenaventura'),
    ('Barrancabermeja', 'Barrancabermeja'),
    ('Tuluá', 'Tuluá'),
    ('Dosquebradas', 'Dosquebradas')
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
        if commit:
            schedule.save()
        return schedule

class SalonRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Usuario", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tucorreo@ejemplo.com'}))
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mínimo 6 caracteres'}))
    password2 = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repite la contraseña'}))
    
    salon_name = forms.CharField(max_length=255, label="Nombre del Negocio", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Barbería Elite'}))
    # AQUI EL CAMBIO IMPORTANTE: ChoiceField para ciudades
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad", widget=forms.Select(attrs={'class': 'form-select'}))
    
    address = forms.CharField(max_length=255, label="Dirección", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle 123 # 45-67'}))
    phone = forms.CharField(max_length=50, label="WhatsApp", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '300 123 4567'})) 
    instagram_link = forms.URLField(required=False, label="Link Instagram", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/tu_negocio'}))
    maps_link = forms.URLField(required=False, label="Link Google Maps", widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://goo.gl/maps/...'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2: raise forms.ValidationError("Las contraseñas no coinciden")
        return p2

class SalonSettingsForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'city', 'address', 'whatsapp_number', 'instagram_link', 'maps_link', 
                  'opening_time', 'closing_time', 'deposit_percentage',
                  'work_monday', 'work_tuesday', 'work_wednesday', 'work_thursday', 'work_friday', 'work_saturday', 'work_sunday']
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
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

# RUTA CORREGIDA: Sin 'pasofinalbacukp/'
with open('apps/businesses/forms.py', 'w', encoding='utf-8') as f:
    f.write(forms_content)
print("✅ forms.py actualizado con lista completa de ciudades.")

# ==========================================
# 2. RESTAURAR REGISTER_OWNER.HTML (DISEÑO BACKUP + CAMPOS NUEVOS)
# ==========================================

register_html = """{% extends 'master.html' %}
{% load static %}
{% block content %}
<style>
    /* Estilos recuperados del Backup para mantener la estética oscura/premium */
    body { background-color: #f8f9fa; }
    .card-header-custom {
        background: linear-gradient(135deg, #000000 0%, #333333 100%);
        color: white;
        text-align: center;
        padding: 3rem 1rem;
    }
    .register-card {
        border: none;
        box-shadow: 0 1rem 3rem rgba(0,0,0,0.175);
        border-radius: 1rem;
        overflow: hidden;
    }
    .form-floating > label { padding-left: 1rem; }
    .btn-dark-custom {
        background-color: #000;
        border: none;
        padding: 1rem;
        font-weight: bold;
        letter-spacing: 1px;
        transition: all 0.3s;
    }
    .btn-dark-custom:hover {
        background-color: #333;
        transform: translateY(-2px);
    }
    .section-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #6c757d;
        font-weight: 700;
        margin: 1.5rem 0 1rem;
        border-bottom: 1px solid #dee2e6;
        padding-bottom: 0.5rem;
    }
</style>

<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-lg-8 col-xl-7">

            <div class="card register-card">
                <div class="card-header-custom">
                    <h2 class="fw-bold mb-1">Únete a Paso Ecosystem</h2>
                    <p class="text-white-50 small mb-0">Lleva tu negocio al siguiente nivel digital.</p>
                </div>

                <div class="card-body p-5 bg-white">
                    <form method="POST">
                        {% csrf_token %}

                        {% if form.errors %}
                            <div class="alert alert-danger small rounded-3 mb-4">
                                <i class="fas fa-exclamation-circle me-1"></i> Por favor corrige los errores abajo.
                                {{ form.non_field_errors }}
                            </div>
                        {% endif %}

                        <div class="section-title">
                            <i class="fas fa-user-circle me-1"></i> Tus Credenciales
                        </div>
                        
                        <div class="row g-3 mb-3">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold">Usuario</label>
                                {{ form.username }}
                                {% if form.username.errors %}<div class="text-danger small">{{ form.username.errors.0 }}</div>{% endif %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold">Email</label>
                                {{ form.email }}
                                {% if form.email.errors %}<div class="text-danger small">{{ form.email.errors.0 }}</div>{% endif %}
                            </div>
                        </div>

                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold">Contraseña</label>
                                {{ form.password1 }}
                                {% if form.password1.errors %}<div class="text-danger small">{{ form.password1.errors.0 }}</div>{% endif %}
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold">Confirmar Contraseña</label>
                                {{ form.password2 }}
                                {% if form.password2.errors %}<div class="text-danger small">{{ form.password2.errors.0 }}</div>{% endif %}
                            </div>
                        </div>

                        <div class="section-title">
                            <i class="fas fa-store me-1"></i> Tu Negocio
                        </div>

                        <div class="mb-3">
                            <label class="form-label small fw-bold">Nombre del Establecimiento</label>
                            {{ form.salon_name }}
                        </div>

                        <div class="row g-3 mb-3">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold">Ciudad</label>
                                {{ form.city }} </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold">Dirección Física</label>
                                {{ form.address }}
                            </div>
                        </div>

                        <div class="input-group mb-3">
                            <span class="input-group-text bg-light border-end-0"><i class="fab fa-whatsapp text-success"></i></span>
                            {{ form.phone }} </div>

                        <div class="row g-3 mb-4">
                            <div class="col-md-6">
                                <div class="input-group">
                                    <span class="input-group-text bg-light border-end-0"><i class="fab fa-instagram text-danger"></i></span>
                                    {{ form.instagram_link }}
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="input-group">
                                    <span class="input-group-text bg-light border-end-0"><i class="fas fa-map-marker-alt text-primary"></i></span>
                                    {{ form.maps_link }}
                                </div>
                            </div>
                        </div>

                        <div class="d-grid gap-2 mt-5">
                            <button type="submit" class="btn btn-dark-custom rounded-pill shadow-sm">
                                CREAR CUENTA EMPRESARIAL <i class="fas fa-arrow-right ms-2"></i>
                            </button>
                        </div>
                    </form>
                </div>

                <div class="card-footer bg-light text-center py-3">
                    <p class="mb-0 text-muted small">
                        ¿Ya tienes cuenta? <a href="{% url 'saas_login' %}" class="fw-bold text-dark text-decoration-none">Inicia Sesión</a>
                    </p>
                </div>
            </div>

            <p class="text-center text-muted mt-4 small">
                <i class="fas fa-lock me-1"></i> Tus datos están protegidos y encriptados.
            </p>
        </div>
    </div>
</div>
{% endblock %}
"""

# RUTA CORREGIDA: Sin 'pasofinalbacukp/'
with open('templates/registration/register_owner.html', 'w', encoding='utf-8') as f:
    f.write(register_html)
print("✅ register_owner.html restaurado con diseño backup y funcionalidad actual.")

# ==========================================
# 3. RESTAURAR LOGIN.HTML (DISEÑO BACKUP + INPUTS MANUALES)
# ==========================================

login_html = """{% extends 'master.html' %}
{% load static %}
{% block content %}
<style>
    /* Estilos recuperados del Backup para el Login */
    body { background-color: #f8f9fa; }
    .login-card {
        border: none;
        box-shadow: 0 1rem 3rem rgba(0,0,0,0.175);
        border-radius: 1rem;
        overflow: hidden;
    }
    .card-header-login {
        background: linear-gradient(135deg, #000000 0%, #333333 100%);
        color: white;
        text-align: center;
        padding: 3rem 1rem;
    }
    .btn-login-custom {
        background-color: #000;
        color: white;
        padding: 0.8rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .btn-login-custom:hover {
        background-color: #333;
        color: #fff;
        transform: translateY(-2px);
    }
</style>

<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">

            <div class="card login-card">
                <div class="card-header-login">
                    <h3 class="fw-bold mb-1">Bienvenido de Nuevo</h3>
                    <p class="text-white-50 small mb-0">Ingresa a tu ecosistema.</p>
                </div>

                <div class="card-body p-5 bg-white">
                    <form method="POST">
                        {% csrf_token %}
                        
                        {% if messages %}
                            {% for message in messages %}
                                <div class="alert alert-{{ message.tags }} small mb-4">{{ message }}</div>
                            {% endfor %}
                        {% endif %}

                        <div class="form-floating mb-3">
                            <input type="text" name="username" class="form-control" id="id_username" placeholder="Usuario" required>
                            <label for="id_username">Usuario</label>
                        </div>

                        <div class="form-floating mb-4">
                            <input type="password" name="password" class="form-control" id="id_password" placeholder="Contraseña" required>
                            <label for="id_password">Contraseña</label>
                        </div>

                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-login-custom rounded-3 shadow-sm">
                                INICIAR SESIÓN <i class="fas fa-arrow-right ms-2"></i>
                            </button>
                        </div>
                    </form>
                </div>

                <div class="card-footer bg-light text-center py-3">
                    <p class="mb-0 text-muted small">
                        ¿Nuevo aquí? <a href="{% url 'register_owner' %}" class="fw-bold text-dark text-decoration-none">Registra tu Negocio</a>
                    </p>
                </div>
            </div>

            <p class="text-center text-muted mt-4 small">
                <i class="fas fa-shield-alt me-1"></i> Acceso Seguro SSL
            </p>
        </div>
    </div>
</div>
{% endblock %}
"""

# RUTA CORREGIDA: Sin 'pasofinalbacukp/'
with open('templates/registration/login.html', 'w', encoding='utf-8') as f:
    f.write(login_html)
print("✅ login.html restaurado con diseño backup y funcionalidad actual.")