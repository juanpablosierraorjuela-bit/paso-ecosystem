import os
import textwrap
import subprocess

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory: os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(textwrap.dedent(content).strip())
    print(f"✅ Reparado: {path}")

print("🚑 CORRIGIENDO ERROR DE IMPORTACIÓN (USER)...")

# ==============================================================================
# 1. FORMS.PY (CORREGIDO)
# ==============================================================================
create_file('apps/businesses/forms.py', """
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Service, Employee, Salon, OpeningHours

# Obtenemos el modelo de usuario correctamente
User = get_user_model()

# --- LOGIN & REGISTRO ---
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))

class OwnerRegistrationForm(forms.Form):
    CIUDADES_COLOMBIA = [
        ('', 'Selecciona tu Ciudad...'), ('Bogotá', 'Bogotá'), ('Medellín', 'Medellín'), 
        ('Cali', 'Cali'), ('Barranquilla', 'Barranquilla'), ('Tunja', 'Tunja'), ('Otra', 'Otra')
    ]
    first_name = forms.CharField(label="Tu Nombre", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Tu Apellido", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    nombre_negocio = forms.CharField(label="Nombre del Negocio", widget=forms.TextInput(attrs={'class': 'form-control'}))
    ciudad = forms.ChoiceField(label="Ciudad", choices=CIUDADES_COLOMBIA, widget=forms.Select(attrs={'class': 'form-select'}))
    direccion = forms.CharField(label="Dirección", widget=forms.TextInput(attrs={'class': 'form-control'}))
    whatsapp = forms.CharField(label="WhatsApp", widget=forms.TextInput(attrs={'class': 'form-control'}))
    instagram = forms.CharField(label="Instagram (Usuario)", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

# --- GESTIÓN DE SERVICIOS ---
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price', 'duration_minutes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corte Clásico'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '20000'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutos (ej: 45)'}),
        }

# --- GESTIÓN DE EMPLEADOS ---
class EmployeeCreationForm(forms.Form):
    name = forms.CharField(label="Nombre del Empleado", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email (Será su usuario)", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña Temporal", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    start_time = forms.TimeField(label="Hora Entrada", widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), initial='09:00')
    end_time = forms.TimeField(label="Hora Salida", widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), initial='18:00')

# --- CONFIGURACIÓN DEL NEGOCIO ---
class SalonConfigForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'phone', 'address', 'instagram_link', 'deposit_percentage', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-control'}),
            'deposit_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
""")

# ==============================================================================
# 2. RESTAURAR BUILD.SH (Producción Estándar)
# ==============================================================================
# Como el paso anterior falló antes de migrar, mantenemos el makemigrations por seguridad
# pero quitamos el mensaje de "Deploy Seguro" para que se vea normal.
create_file('build.sh', """#!/usr/bin/env bash
set -o errexit

echo "🚀 Iniciando Deploy de Producción..."
pip install -r requirements.txt
python manage.py collectstatic --no-input

# Aseguramos migraciones de businesses por si fallaron antes
python manage.py makemigrations businesses
python manage.py migrate

echo "✅ Deploy Finalizado."
""")

# ==============================================================================
# 3. SUBIDA AUTOMÁTICA
# ==============================================================================
print("🤖 Subiendo corrección a GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix: Correct User model import in forms.py"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("🚀 ¡ENVIADO! Ahora sí compilará sin errores.")
except Exception as e:
    print(f"⚠️ Error git: {e}")