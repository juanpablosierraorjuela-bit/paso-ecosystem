import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# 1. FORMS.PY (ESTILOS DESDE PYTHON)
# ==========================================
# Agregamos un método __init__ para inyectar clases CSS a todos los campos
forms_content = """
from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.core.models import User
from apps.businesses.models import Salon
from datetime import time

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
    ('Tunja', 'Tunja'),
    ('Montería', 'Montería'),
    ('Valledupar', 'Valledupar'),
    ('Armenia', 'Armenia'),
    ('Neiva', 'Neiva'),
    ('Popayán', 'Popayán'),
    ('Sincelejo', 'Sincelejo'),
    ('Riohacha', 'Riohacha'),
    ('Zipaquirá', 'Zipaquirá'),
    ('Soacha', 'Soacha'),
    ('Envigado', 'Envigado'),
    ('Itagüí', 'Itagüí'),
    ('Bello', 'Bello'),
    ('Otro', 'Otro (Escribir en dirección)'),
]

class OwnerRegistrationForm(UserCreationForm):
    # --- Datos del Dueño ---
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")
    email = forms.EmailField(required=True, label="Correo Electrónico", help_text="Recibirás tu validación aquí.")
    phone = forms.CharField(max_length=20, required=True, label="WhatsApp Personal")
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad Base")

    # --- Datos del Negocio (Salón) ---
    salon_name = forms.CharField(max_length=150, required=True, label="Nombre del Negocio")
    salon_address = forms.CharField(max_length=255, required=True, label="Dirección Física")
    
    instagram_url = forms.URLField(required=False, label="Link de Instagram (Opcional)")
    google_maps_url = forms.URLField(required=False, label="Link de Google Maps (Opcional)")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'city')

    def __init__(self, *args, **kwargs):
        super(OwnerRegistrationForm, self).__init__(*args, **kwargs)
        # ESTILO "LUXURY" AUTOMÁTICO
        # Recorremos todos los campos y les ponemos la clase de Tailwind
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-black focus:border-black sm:text-sm'
            
            # Placeholder inteligente
            if field.label:
                field.widget.attrs['placeholder'] = field.label

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'OWNER'
        user.is_verified_payment = False
        if commit:
            user.save()

        Salon.objects.create(
            owner=user,
            name=self.cleaned_data['salon_name'],
            city=self.cleaned_data['city'],
            address=self.cleaned_data['salon_address'],
            instagram_url=self.cleaned_data.get('instagram_url', ''),
            google_maps_url=self.cleaned_data.get('google_maps_url', ''),
            opening_time=time(9, 0),
            closing_time=time(20, 0),
            deposit_percentage=50
        )
        return user
"""

# ==========================================
# 2. HTML (LAYOUT LIMPIO Y ORDENADO)
# ==========================================
html_content = """
{% extends 'base.html' %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-3xl w-full space-y-8 bg-white p-10 rounded-2xl shadow-xl border border-gray-100">
        <div class="text-center">
            <h2 class="mt-2 text-3xl font-serif text-gray-900">
                Únete al Ecosistema
            </h2>
            <p class="mt-2 text-sm text-gray-500">
                Configura tu perfil de dueño y tu negocio en un solo paso.
            </p>
        </div>
        
        <form class="mt-8 space-y-8" method="POST">
            {% csrf_token %}
            
            {% if form.errors %}
                <div class="bg-red-50 border-l-4 border-red-500 p-4 mb-4 rounded-r">
                    <p class="text-red-700 font-bold text-sm">Hay errores en el formulario:</p>
                    <ul class="list-disc ml-5 text-xs text-red-600 mt-1">
                        {% for field in form %}
                            {% for error in field.errors %}
                                <li>{{ field.label }}: {{ error }}</li>
                            {% endfor %}
                        {% endfor %}
                        {% for error in form.non_field_errors %}
                            <li>{{ error }}</li>
                        {% endfor %}
                    </ul>
                </div>
            {% endif %}

            <div>
                <h3 class="text-lg font-bold text-gray-800 border-b pb-2 mb-4">1. El Dueño</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
                        {{ form.first_name }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Apellido</label>
                        {{ form.last_name }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">WhatsApp</label>
                        {{ form.phone }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Ciudad Base</label>
                        {{ form.city }}
                    </div>
                </div>
            </div>

            <div>
                <h3 class="text-lg font-bold text-gray-800 border-b pb-2 mb-4">2. El Negocio</h3>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Nombre del Salón / Barbería</label>
                        {{ form.salon_name }}
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Dirección Física</label>
                        {{ form.salon_address }}
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Instagram (Opcional)</label>
                            {{ form.instagram_url }}
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Google Maps (Opcional)</label>
                            {{ form.google_maps_url }}
                        </div>
                    </div>
                </div>
            </div>

            <div class="bg-gray-50 p-6 rounded-xl">
                <h3 class="text-lg font-bold text-gray-800 border-b pb-2 mb-4">3. Seguridad</h3>
                <div class="grid grid-cols-1 gap-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Usuario (Para Login)</label>
                        {{ form.username }}
                        <p class="text-xs text-gray-400 mt-1">{{ form.username.help_text }}</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Correo Electrónico</label>
                        {{ form.email }}
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
                            {{ form.password1 }} 
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Confirmar Contraseña</label>
                            {{ form.password2 }}
                        </div>
                    </div>
                </div>
            </div>

            <div>
                <button type="submit" class="w-full flex justify-center py-4 px-4 border border-transparent text-sm font-bold rounded-md text-white bg-black hover:bg-gray-800 focus:outline-none transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">
                    🚀 REGISTRAR ECOSISTEMA
                </button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 3. EJECUTAR
# ==========================================
def apply_fix():
    print("🎨 APLICANDO CORRECCIONES VISUALES...")

    # Actualizar Forms
    with open(BASE_DIR / 'apps' / 'core' / 'forms.py', 'w', encoding='utf-8') as f:
        f.write(forms_content.strip())
    print("✅ apps/core/forms.py actualizado (Estilos inyectados).")

    # Actualizar HTML
    with open(BASE_DIR / 'templates' / 'registration' / 'register_owner.html', 'w', encoding='utf-8') as f:
        f.write(html_content.strip())
    print("✅ templates/registration/register_owner.html rediseñado (Grid limpio).")

if __name__ == "__main__":
    apply_fix()
    print("\n✨ LISTO. Reinicia el servidor y mira la magia.")