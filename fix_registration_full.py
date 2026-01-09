import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. EL LISTADO DE CIUDADES (Dropdown)
# ==========================================
# Lista condensada de principales ciudades para no hacer el archivo eterno, 
# pero cubre la mayoría del mercado inicial.
CITIES_LIST = [
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
    ('Tunja', 'Tunja'),
    ('Montería', 'Montería'),
    ('Valledupar', 'Valledupar'),
    ('Armenia', 'Armenia'),
    ('Neiva', 'Neiva'),
    ('Popayán', 'Popayán'),
    ('Sincelejo', 'Sincelejo'),
    ('Riohacha', 'Riohacha'),
    ('Tunja', 'Tunja'),
    ('Zipaquirá', 'Zipaquirá'),
    ('Soacha', 'Soacha'),
    ('Envigado', 'Envigado'),
    ('Itagüí', 'Itagüí'),
    ('Bello', 'Bello'),
    ('Otro', 'Otro (Escribir en dirección)'),
]

# ==========================================
# 2. CONTENIDO PARA FORMS.PY
# ==========================================
forms_content = f"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.core.models import User
from apps.businesses.models import Salon
from datetime import time

COLOMBIA_CITIES = {CITIES_LIST}

class OwnerRegistrationForm(UserCreationForm):
    # --- Datos del Dueño ---
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")
    email = forms.EmailField(required=True, label="Correo Electrónico", help_text="Recibirás tu validación aquí.")
    phone = forms.CharField(max_length=20, required=True, label="WhatsApp Personal / Soporte")
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad Base")

    # --- Datos del Negocio (Salón) ---
    salon_name = forms.CharField(max_length=150, required=True, label="Nombre del Negocio")
    salon_address = forms.CharField(max_length=255, required=True, label="Dirección Física")
    
    # --- Redes y Marketing ---
    instagram_url = forms.URLField(required=False, label="Link de Instagram (Opcional)", widget=forms.URLInput(attrs={{'placeholder': 'https://instagram.com/tu_negocio'}}))
    google_maps_url = forms.URLField(required=False, label="Link de Google Maps (Opcional)", widget=forms.URLInput(attrs={{'placeholder': 'https://maps.google.com/...'}}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'city')

    def save(self, commit=True):
        # 1. Guardar el Usuario (Dueño)
        user = super().save(commit=False)
        user.role = 'OWNER'
        user.is_verified_payment = False # Empieza sin pagar
        if commit:
            user.save()

        # 2. Crear el Negocio (Salón) automáticamente
        # Se establecen horarios por defecto (9am - 8pm) que luego pueden editar
        Salon.objects.create(
            owner=user,
            name=self.cleaned_data['salon_name'],
            city=self.cleaned_data['city'],
            address=self.cleaned_data['salon_address'],
            instagram_url=self.cleaned_data.get('instagram_url', ''),
            google_maps_url=self.cleaned_data.get('google_maps_url', ''),
            opening_time=time(9, 0),  # Default apertura
            closing_time=time(20, 0), # Default cierre
            deposit_percentage=50
        )
        return user
"""

# ==========================================
# 3. CONTENIDO PARA VIEWS.PY (Apps/Core)
# ==========================================
views_content = """
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import OwnerRegistrationForm

def home(request):
    return render(request, 'home.html')

def register_owner(request):
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Iniciar sesión automáticamente
            login(request, user)
            messages.success(request, '¡Bienvenido! Tu ecosistema ha sido creado. Tienes 24h para activarlo.')
            return redirect('dashboard') # Redirige al panel de dueño
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = OwnerRegistrationForm()
    
    return render(request, 'registration/register_owner.html', {'form': form})

def login_view(request):
    return render(request, 'registration/login.html')
"""

# ==========================================
# 4. CONTENIDO PARA EL TEMPLATE (HTML)
# ==========================================
html_content = """
{% extends 'base.html' %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-2xl w-full space-y-8 bg-white p-10 rounded-2xl shadow-xl border border-gray-100">
        <div class="text-center">
            <h2 class="mt-2 text-3xl font-serif text-gray-900">
                Crea tu Ecosistema
            </h2>
            <p class="mt-2 text-sm text-gray-500">
                Únete a la plataforma exclusiva para negocios de belleza.
            </p>
        </div>
        
        <form class="mt-8 space-y-6" method="POST">
            {% csrf_token %}
            
            {% if form.errors %}
                <div class="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
                    <p class="text-red-700 font-bold">Por favor corrige los siguientes errores:</p>
                    {{ form.errors }}
                </div>
            {% endif %}

            <div class="bg-gray-50 p-4 rounded-lg mb-6">
                <h3 class="text-lg font-bold text-gray-700 mb-4 border-b pb-2">1. Tus Credenciales</h3>
                <div class="grid grid-cols-1 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Usuario (Para entrar)</label>
                        {{ form.username }}
                        <span class="text-xs text-gray-400">{{ form.username.help_text }}</span>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Contraseña</label>
                            {{ form.as_div.password1 }} 
                            </div>
                    </div>
                </div>
            </div>

            <div class="space-y-4">
                {% for field in form %}
                    {% if field.name != 'username' %} <div>
                        <label for="{{ field.id_for_label }}" class="block text-sm font-medium text-gray-700">
                            {{ field.label }}
                        </label>
                        <div class="mt-1">
                            <input type="{{ field.field.widget.input_type }}" 
                                   name="{{ field.name }}" 
                                   id="{{ field.id_for_label }}"
                                   {% if field.value %}value="{{ field.value }}"{% endif %}
                                   {% if field.field.required %}required{% endif %}
                                   class="appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-black focus:border-black sm:text-sm"
                                   {% if field.name == 'city' %}list="cities"{% endif %}
                            >
                            
                            {% if field.name == 'city' %}
                                <select name="{{ field.name }}" id="{{ field.id_for_label }}" class="block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-black focus:border-black sm:text-sm">
                                    {% for value, text in field.field.choices %}
                                        <option value="{{ value }}" {% if field.value == value %}selected{% endif %}>{{ text }}</option>
                                    {% endfor %}
                                </select>
                                {% endif %}
                        </div>
                        {% if field.help_text %}
                            <p class="mt-2 text-xs text-gray-500">{{ field.help_text }}</p>
                        {% endif %}
                        {% if field.errors %}
                            <p class="mt-2 text-sm text-red-600">{{ field.errors.0 }}</p>
                        {% endif %}
                    </div>
                    {% endif %}
                {% endfor %}
            </div>

            <div>
                <button type="submit" class="group relative w-full flex justify-center py-4 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-black hover:bg-gray-800 focus:outline-none transition-colors shadow-lg">
                    Registrar mi Negocio
                </button>
            </div>
            
            <div class="text-center mt-4">
                <a href="{% url 'login' %}" class="text-sm text-gray-500 hover:text-black underline">¿Ya tienes cuenta? Inicia Sesión</a>
            </div>
        </form>
    </div>
</div>

<script>
    // Pequeño script para limpiar campos duplicados visualmente si el loop genera doble input para city
    // (En este template manual, el 'if field.name == city' evita el input text y pone el select)
    // Este script asegura que los inputs tengan estilo consistente
    document.querySelectorAll('input, select').forEach(el => {
        if (!el.classList.contains('appearance-none')) {
            el.classList.add('appearance-none', 'block', 'w-full', 'px-3', 'py-3', 'border', 'border-gray-300', 'rounded-md', 'shadow-sm', 'placeholder-gray-400', 'focus:outline-none', 'focus:ring-black', 'focus:border-black', 'sm:text-sm');
        }
        // UserCreationForm pone help_text de password muy largo, lo ocultamos visualmente si molesta
    });
</script>
{% endblock %}
"""

# ==========================================
# 5. EJECUTAR LOS CAMBIOS
# ==========================================
def apply_fix():
    print("🛠️  ACTUALIZANDO SISTEMA DE REGISTRO...")

    # 1. Actualizar forms.py
    with open(BASE_DIR / 'apps' / 'core' / 'forms.py', 'w', encoding='utf-8') as f:
        f.write(forms_content.strip())
    print("✅ apps/core/forms.py: Formulario con Salón y Ciudades añadido.")

    # 2. Actualizar views.py
    with open(BASE_DIR / 'apps' / 'core' / 'views.py', 'w', encoding='utf-8') as f:
        f.write(views_content.strip())
    print("✅ apps/core/views.py: Lógica de guardado activada.")

    # 3. Actualizar Template HTML
    with open(BASE_DIR / 'templates' / 'registration' / 'register_owner.html', 'w', encoding='utf-8') as f:
        f.write(html_content.strip())
    print("✅ templates/registration/register_owner.html: Diseño visual aplicado.")

if __name__ == "__main__":
    apply_fix()
    print("\n🚀 LISTO! Ahora sigue estos pasos:")
    print("1. Ejecuta: python manage.py runserver")
    print("2. Ve a http://127.0.0.1:8000/registro-dueno/")
    print("3. Verás el formulario completo. ¡Pruébalo!")