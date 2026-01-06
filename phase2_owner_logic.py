import os

# ==========================================
# 1. FORMULARIOS (VALIDACIÓN DE DATOS)
# ==========================================
forms_content = """
from django import forms
from django.contrib.auth import get_user_model
from .models import Salon

User = get_user_model()

# Lista de Ciudades Principales (Placeholder para el ejemplo, en prod usaríamos JSON completo)
CIUDADES_COLOMBIA = [
    ('Bogotá', 'Bogotá D.C.'), ('Medellín', 'Medellín'), ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'), ('Cartagena', 'Cartagena'), ('Tunja', 'Tunja'),
    ('Bucaramanga', 'Bucaramanga'), ('Pereira', 'Pereira'), ('Manizales', 'Manizales'),
]

class OwnerRegistrationForm(forms.ModelForm):
    # Campos de Usuario
    email = forms.EmailField(label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '******'}))
    phone = forms.CharField(label="WhatsApp Personal", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '300...'}))
    
    # Campos de Negocio
    salon_name = forms.CharField(label="Nombre del Negocio", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Barbería Vikingos'}))
    city = forms.ChoiceField(label="Ciudad", choices=CIUDADES_COLOMBIA, widget=forms.Select(attrs={'class': 'form-select'}))
    address = forms.CharField(label="Dirección", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cra 15 # 12-34'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu Apellido'}),
        }

    def save(self, commit=True):
        # 1. Crear Usuario
        user = super().save(commit=False)
        user.username = self.cleaned_data['email'] # Usamos email como usuario
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        user.role = 'OWNER'
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
            
            # 2. Crear Salón Vinculado
            Salon.objects.create(
                owner=user,
                name=self.cleaned_data['salon_name'],
                city=self.cleaned_data['city'],
                address=self.cleaned_data['address']
            )
        return user
"""

# ==========================================
# 2. VISTAS (LÓGICA DEL DUEÑO)
# ==========================================
# Actualizamos apps/businesses/views.py
biz_views = """
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Salon
from apps.core.models import GlobalSettings

@login_required
def owner_dashboard(request):
    # Seguridad: Solo dueños
    if request.user.role != 'OWNER':
        return redirect('home')
        
    user = request.user
    salon = getattr(user, 'salon', None)
    settings = GlobalSettings.objects.first()
    
    # 1. Lógica del "Reaper" (Tiempo Restante)
    hours_since = user.hours_since_registration()
    hours_remaining = 24 - hours_since
    is_expired = hours_remaining <= 0 and not user.is_verified_payment
    
    # 2. Mensaje de WhatsApp para Activación
    wa_message = f"Hola PASO, soy {user.first_name} (ID: {user.id}). Quiero activar mi ecosistema para {salon.name if salon else 'mi negocio'}."
    wa_link = f"https://wa.me/{settings.support_whatsapp}?text={wa_message}" if settings else "#"

    context = {
        'salon': salon,
        'hours_remaining': max(0, int(hours_remaining)),
        'hours_percent': (max(0, hours_remaining) / 24) * 100,
        'is_verified': user.is_verified_payment,
        'is_expired': is_expired,
        'wa_link': wa_link
    }
    return render(request, 'businesses/dashboard.html', context)
"""

# Actualizamos apps/core/views.py para el registro
core_views = """
from django.shortcuts import render, redirect
from django.contrib.auth import login
from apps.businesses.forms import OwnerRegistrationForm

def home(request):
    return render(request, 'home.html')

def register_owner(request):
    if request.user.is_authenticated:
        return redirect('businesses:dashboard')
        
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto-login
            return redirect('businesses:dashboard')
    else:
        form = OwnerRegistrationForm()
        
    return render(request, 'registration/register_owner.html', {'form': form})

def login_view(request):
    # Placeholder login logic (Django auth views should be used in prod urls)
    from django.contrib.auth.views import LoginView
    return LoginView.as_view(template_name='registration/login.html')(request)
"""

# ==========================================
# 3. URLS (RUTEO)
# ==========================================
biz_urls = """
from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('dashboard/', views.owner_dashboard, name='dashboard'),
]
"""

# ==========================================
# 4. TEMPLATES (DISEÑO DE LUJO)
# ==========================================

# Template: Registro Dueño
tpl_register = """
{% extends 'base.html' %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8 col-lg-6">
        <div class="card bg-dark text-white border-secondary shadow-lg mt-5">
            <div class="card-body p-5">
                <h2 class="text-center mb-4" style="color: #d4af37;">Registro de Aliado</h2>
                <p class="text-center text-muted mb-4">Únete a la élite de la belleza en Colombia.</p>
                
                <form method="post">
                    {% csrf_token %}
                    
                    <h5 class="mt-4 mb-3 border-bottom border-secondary pb-2">Datos Personales</h5>
                    <div class="row">
                        <div class="col-6 mb-3">{{ form.first_name.label_tag }} {{ form.first_name }}</div>
                        <div class="col-6 mb-3">{{ form.last_name.label_tag }} {{ form.last_name }}</div>
                    </div>
                    <div class="mb-3">{{ form.email.label_tag }} {{ form.email }}</div>
                    <div class="mb-3">{{ form.phone.label_tag }} {{ form.phone }}</div>
                    
                    <h5 class="mt-4 mb-3 border-bottom border-secondary pb-2">Datos del Negocio</h5>
                    <div class="mb-3">{{ form.salon_name.label_tag }} {{ form.salon_name }}</div>
                    <div class="row">
                        <div class="col-6 mb-3">{{ form.city.label_tag }} {{ form.city }}</div>
                        <div class="col-6 mb-3">{{ form.address.label_tag }} {{ form.address }}</div>
                    </div>
                    
                    <div class="mb-4">{{ form.password.label_tag }} {{ form.password }}</div>
                    
                    <button type="submit" class="btn btn-warning w-100 py-3 fw-bold" style="background-color: #d4af37; border: none;">
                        🚀 CREAR MI ECOSISTEMA
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# Template: Dashboard Dueño
tpl_dashboard = """
{% extends 'base.html' %}
{% block content %}
<div class="container py-5">
    <div class="d-flex justify-content-between align-items-center mb-5">
        <div>
            <h1 class="fw-bold">Hola, {{ user.first_name }}</h1>
            <p class="text-secondary">{{ salon.name }} | {{ salon.get_city_display }}</p>
        </div>
        <div class="text-end">
            <span class="badge {% if is_verified %}bg-success{% else %}bg-warning text-dark{% endif %} p-2">
                {% if is_verified %}Cuenta Verificada{% else %}Pago Pendiente{% endif %}
            </span>
        </div>
    </div>

    {% if not is_verified %}
    <div class="card mb-5 border-warning" style="background: rgba(212, 175, 55, 0.1);">
        <div class="card-body d-flex justify-content-between align-items-center">
            <div>
                <h4 class="text-warning">⚠️ Activación Requerida</h4>
                <p class="mb-0">Tu ecosistema está en modo prueba. Tienes <strong>{{ hours_remaining }} horas</strong> para activar tu cuenta.</p>
            </div>
            <a href="{{ wa_link }}" target="_blank" class="btn btn-warning fw-bold">
                📲 Activar por WhatsApp ($50k)
            </a>
        </div>
        <div class="progress" style="height: 5px;">
            <div class="progress-bar bg-warning" role="progressbar" style="width: {{ hours_percent }}%;"></div>
        </div>
    </div>
    {% endif %}

    <div class="row g-4">
        <div class="col-md-3">
            <div class="card bg-dark border-secondary h-100">
                <div class="card-body text-center">
                    <h3 class="display-4 fw-bold text-white">0</h3>
                    <p class="text-muted">Citas Hoy</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-dark border-secondary h-100">
                <div class="card-body text-center">
                    <h3 class="display-4 fw-bold text-white">0</h3>
                    <p class="text-muted">Empleados Activos</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-dark border-secondary h-100">
                <div class="card-body text-center">
                    <h3 class="display-4 fw-bold text-white">$0</h3>
                    <p class="text-muted">Ventas del Mes</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-dark border-secondary h-100" style="border-style: dashed !important;">
                <div class="card-body text-center d-flex flex-column justify-content-center">
                    <a href="#" class="text-decoration-none text-warning stretched-link">+ Nuevo Servicio</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

def main():
    print("🚀 INYECTANDO LÓGICA DE FASE 2 (Dueños)...")
    
    # Escribir Forms
    with open('apps/businesses/forms.py', 'w', encoding='utf-8') as f:
        f.write(forms_content)
    
    # Escribir Views
    with open('apps/businesses/views.py', 'w', encoding='utf-8') as f:
        f.write(biz_views)
    with open('apps/core/views.py', 'w', encoding='utf-8') as f:
        f.write(core_views)
        
    # Escribir URLs
    with open('apps/businesses/urls.py', 'w', encoding='utf-8') as f:
        f.write(biz_urls)
        
    # Escribir Templates
    os.makedirs('templates/registration', exist_ok=True)
    with open('templates/registration/register_owner.html', 'w', encoding='utf-8') as f:
        f.write(tpl_register)
        
    os.makedirs('templates/businesses', exist_ok=True)
    with open('templates/businesses/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(tpl_dashboard)
        
    print("✅ Fase 2 Completada: Registro y Dashboard listos.")
    print("👉 EJECUTA AHORA:")
    print("   git add .")
    print("   git commit -m 'Implement Owner Logic: Registration and Dashboard'")
    print("   git push origin main")

if __name__ == "__main__":
    main()