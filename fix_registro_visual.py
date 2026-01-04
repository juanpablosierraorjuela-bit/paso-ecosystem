import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates", "registration")
FORMS_PATH = os.path.join(APP_DIR, "forms.py")
REGISTER_HTML_PATH = os.path.join(TEMPLATES_DIR, "register_owner.html")

# --- 1. FORMS.PY MEJORADO (CON CAJAS DE TEXTO Y TODOS LOS CAMPOS) ---
CONTENIDO_FORMS = """from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee, SalonSchedule

User = get_user_model()

# --- 1. REGISTRO DUEÑO ---
class OwnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Crea tu contraseña'}), label="Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repite la contraseña'}), label="Confirmar")
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario para login'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("password_confirm"):
            raise forms.ValidationError("Las contraseñas no coinciden.")

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        # Aseguramos que address (Maps) e instagram estén aquí
        fields = ['name', 'address', 'city', 'phone', 'whatsapp', 'instagram']
        labels = {
            'name': 'Nombre del Negocio',
            'address': 'Dirección (Ubicación en Maps)',
            'city': 'Ciudad',
            'phone': 'Teléfono de Contacto',
            'whatsapp': 'WhatsApp (Para reservas)',
            'instagram': 'Usuario de Instagram (Sin @)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Barbería El Rey'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Calle 123 # 45-67'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bogotá'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 300 123 4567'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 300 123 4567'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: barberia_elrey'}),
        }

# --- 2. GESTIÓN SERVICIOS ---
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# --- 3. GESTIÓN EMPLEADOS ---
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'phone', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class EmployeeCreationForm(forms.ModelForm):
    username = forms.CharField(label="Usuario de Acceso", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña Temporal", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'phone', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

# --- 4. CONFIGURACIÓN HORARIOS ---
class SalonScheduleForm(forms.ModelForm):
    class Meta:
        model = SalonSchedule
        fields = ['monday_open', 'tuesday_open', 'wednesday_open', 'thursday_open', 'friday_open', 'saturday_open', 'sunday_open']
"""

# --- 2. HTML REGISTER_OWNER.HTML (VISUALIZACIÓN COMPLETA) ---
CONTENIDO_HTML = """{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
            <div class="card shadow-lg border-0 rounded-4">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <h2 class="fw-bold text-dark">Registra tu Negocio</h2>
                        <p class="text-muted">Únete al ecosistema y digitaliza tu agenda.</p>
                    </div>

                    <form method="post">
                        {% csrf_token %}
                        
                        {% if user_form.errors or salon_form.errors %}
                            <div class="alert alert-danger">
                                Por favor corrige los errores indicados abajo.
                            </div>
                        {% endif %}

                        <h5 class="text-uppercase text-primary fw-bold small mb-3 border-bottom pb-2">1. Datos del Dueño</h5>
                        
                        <div class="row mb-3">
                            <div class="col-6">
                                <label class="form-label fw-bold small">Nombre</label>
                                {{ user_form.first_name }}
                            </div>
                            <div class="col-6">
                                <label class="form-label fw-bold small">Apellido</label>
                                {{ user_form.last_name }}
                            </div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label fw-bold small">Correo Electrónico</label>
                            {{ user_form.email }}
                        </div>

                        <div class="mb-3">
                            <label class="form-label fw-bold small">Usuario (Login)</label>
                            {{ user_form.username }}
                        </div>

                        <div class="row mb-4">
                            <div class="col-6">
                                <label class="form-label fw-bold small">Contraseña</label>
                                {{ user_form.password }}
                            </div>
                            <div class="col-6">
                                <label class="form-label fw-bold small">Confirmar</label>
                                {{ user_form.password_confirm }}
                            </div>
                        </div>

                        <h5 class="text-uppercase text-success fw-bold small mb-3 border-bottom pb-2">2. Datos del Negocio</h5>

                        <div class="mb-3">
                            <label class="form-label fw-bold small">Nombre del Negocio</label>
                            {{ salon_form.name }}
                        </div>
                        
                        <div class="row mb-3">
                            <div class="col-6">
                                <label class="form-label fw-bold small">Ciudad</label>
                                {{ salon_form.city }}
                            </div>
                            <div class="col-6">
                                <label class="form-label fw-bold small">Teléfono</label>
                                {{ salon_form.phone }}
                            </div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label fw-bold small">Dirección (Maps)</label>
                            {{ salon_form.address }}
                            <div class="form-text small">La dirección exacta para que te encuentren en el mapa.</div>
                        </div>

                        <div class="row mb-4">
                            <div class="col-6">
                                <label class="form-label fw-bold small text-success"><i class="bi bi-whatsapp"></i> WhatsApp</label>
                                {{ salon_form.whatsapp }}
                            </div>
                            <div class="col-6">
                                <label class="form-label fw-bold small text-danger"><i class="bi bi-instagram"></i> Instagram</label>
                                {{ salon_form.instagram }}
                            </div>
                        </div>

                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-dark btn-lg fw-bold rounded-pill">
                                Crear Cuenta y Negocio
                            </button>
                            <a href="{% url 'login' %}" class="btn btn-outline-secondary btn-sm rounded-pill mt-2">
                                ¿Ya tienes cuenta? Inicia Sesión
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

def aplicar_fix_visual():
    print("🎨 Mejorando forms.py con widgets visuales...")
    with open(FORMS_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_FORMS)

    print("🖼️ Rediseñando register_owner.html con todos los campos...")
    with open(REGISTER_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_HTML)
        
    print("✅ ¡Formulario reparado! Ahora tiene cajas de texto, Instagram y Maps.")

if __name__ == "__main__":
    aplicar_fix_visual()