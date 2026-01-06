import os
import subprocess

# --- 1. BASE DE DATOS DE CIUDADES (Estándar DANE) ---
colombia_data_content = """
# Lista simplificada para el prototipo. 
# En producción podemos cargar el JSON completo de 1.101 municipios.

COLOMBIA_CITIES = [
    ('', 'Selecciona tu Ciudad...'),
    ('Bogotá D.C.', 'Bogotá D.C.'),
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
    ('Popayán', 'Popayán'),
    ('Tunja', 'Tunja'),
    ('Neiva', 'Neiva'),
    ('Armenia', 'Armenia'),
    ('Soacha', 'Soacha'),
    ('Bello', 'Bello'),
    ('Itagüí', 'Itagüí'),
    ('Envigado', 'Envigado'),
    # ... Se pueden agregar más aquí
]
"""

# --- 2. FORMULARIO DE REGISTRO INTELIGENTE ---
forms_content = """from django import forms
from django.contrib.auth import get_user_model
from .utils.colombia_data import COLOMBIA_CITIES

User = get_user_model()

class OwnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Contraseña segura'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Confirmar contraseña'
    }))
    
    # Campos del Negocio (Se guardarán en BusinessProfile después)
    business_name = forms.CharField(
        label="Nombre del Negocio",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Barbería Vikingos'})
    )
    address = forms.CharField(
        label="Dirección",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle 123 # 45-67'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'city']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario único'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '300 123 4567'}),
            'city': forms.Select(choices=COLOMBIA_CITIES, attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
"""

# --- 3. DASHBOARD CON TEMPORIZADOR DE LA MUERTE (JS) ---
dashboard_content = """{% extends 'businesses/base_dashboard.html' %}
{% block content %}

<div class="container-fluid py-4">
    
    {% if not user.is_verified_payment %}
    <div class="alert alert-warning border-0 shadow-sm mb-4" role="alert" style="background: linear-gradient(90deg, #fff3cd 0%, #fff8e1 100%);">
        <div class="d-flex align-items-center justify-content-between flex-wrap gap-3">
            <div class="d-flex align-items-center">
                <div class="display-4 me-3">⚠️</div>
                <div>
                    <h4 class="alert-heading fw-bold mb-1">¡Activa tu Ecosistema!</h4>
                    <p class="mb-0">Tu cuenta está en periodo de prueba. Realiza el pago para evitar la eliminación.</p>
                </div>
            </div>
            
            <div class="text-end">
                <div class="text-uppercase small text-muted fw-bold ls-1">Tiempo Restante</div>
                <div id="death-timer" class="display-6 fw-bold text-danger">Calculando...</div>
            </div>

            <div>
                <a href="https://wa.me/{{ global_settings.support_whatsapp }}?text=Hola%20PASO,%20quiero%20activar%20mi%20cuenta%20ID:%20{{ user.username }}" 
                   target="_blank" 
                   class="btn btn-success btn-lg px-4 shadow-sm">
                   <i class="fab fa-whatsapp me-2"></i> Pagar $50k Ahora
                </a>
            </div>
        </div>
    </div>
    {% endif %}

    <div class="row g-4 mb-4">
        <div class="col-md-3">
            <div class="card h-100 border-0 shadow-sm hover-scale">
                <div class="card-body">
                    <h6 class="text-muted text-uppercase mb-2">Empleados</h6>
                    <h2 class="display-5 fw-bold text-primary">0</h2>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card h-100 border-0 shadow-sm hover-scale">
                <div class="card-body">
                    <h6 class="text-muted text-uppercase mb-2">Citas Hoy</h6>
                    <h2 class="display-5 fw-bold text-success">0</h2>
                </div>
            </div>
        </div>
        </div>

</div>

<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Obtenemos la fecha de registro desde Django
        const regDateStr = "{{ user.registration_timestamp|date:'Y-m-d H:i:s' }}"; 
        const regDate = new Date(regDateStr);
        
        // Calculamos la fecha de muerte (Registro + 24 horas)
        const deathDate = new Date(regDate.getTime() + (24 * 60 * 60 * 1000));

        function updateTimer() {
            const now = new Date().getTime();
            const distance = deathDate - now;

            if (distance < 0) {
                document.getElementById("death-timer").innerHTML = "EXPIRADO";
                document.getElementById("death-timer").classList.add("text-dark");
                return;
            }

            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            document.getElementById("death-timer").innerHTML = 
                (hours < 10 ? "0" + hours : hours) + ":" + 
                (minutes < 10 ? "0" + minutes : minutes) + ":" + 
                (seconds < 10 ? "0" + seconds : seconds);
        }

        setInterval(updateTimer, 1000);
        updateTimer();
    });
</script>

<style>
    .hover-scale { transition: transform 0.2s; }
    .hover-scale:hover { transform: translateY(-5px); }
    .ls-1 { letter-spacing: 1px; }
</style>
{% endblock %}
"""

# --- FUNCIONES ---
def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Archivo creado: {path}")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    print("🚀 Iniciando FASE 2: Dueño de Negocio...")
    
    write_file('apps/core/utils/colombia_data.py', colombia_data_content)
    write_file('apps/core/forms.py', forms_content)
    write_file('templates/businesses/dashboard.html', dashboard_content)
    
    # Git Push automático
    try:
        print("🐙 Subiendo cambios a GitHub...")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "feat: Phase 2 - Cities DB, Smart Form & Death Timer"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ ¡FASE 2 DESPLEGADA!")
    except Exception as e:
        print(f"⚠️ Error Git: {e}")
    
    # Autodestrucción
    try:
        os.remove(__file__)
    except:
        pass