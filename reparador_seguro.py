import os
import shutil
import sys

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
MODELS_PATH = os.path.join(APP_DIR, "models.py")
FORMS_PATH = os.path.join(APP_DIR, "forms.py")
ADMIN_PATH = os.path.join(APP_DIR, "admin.py")

# --- 1. CONTENIDO CORRECTO DE MODELOS (MODELS.PY) ---
# Este contenido incluye TODO: Salon, Service (con duración), Employee y Schedule.
CONTENIDO_MODELS = """from django.db import models
from django.conf import settings

class Salon(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salon')
    name = models.CharField(max_length=255, verbose_name="Nombre del Negocio")
    description = models.TextField(verbose_name="Descripción", blank=True)
    
    # Datos de contacto
    address = models.CharField(max_length=255, verbose_name="Dirección Física")
    phone = models.CharField(max_length=50, verbose_name="Teléfono", blank=True, default='')
    email = models.EmailField(verbose_name="Correo del Negocio", blank=True)
    
    # Redes Sociales
    whatsapp = models.CharField(max_length=50, blank=True, verbose_name="WhatsApp")
    instagram = models.CharField(max_length=100, blank=True, verbose_name="Instagram")

    def __str__(self):
        return self.name

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100, verbose_name="Nombre del Servicio")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # --- CAMPO NUEVO BLINDADO ---
    duration_minutes = models.IntegerField(default=30, verbose_name="Duración (min)")
    # ----------------------------
    
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Precio")

    def __str__(self):
        return self.name

class Employee(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='employees')
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellido")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class SalonSchedule(models.Model):
    salon = models.OneToOneField(Salon, on_delete=models.CASCADE, related_name='schedule')
    monday_open = models.BooleanField(default=True, verbose_name="Lunes")
    tuesday_open = models.BooleanField(default=True, verbose_name="Martes")
    wednesday_open = models.BooleanField(default=True, verbose_name="Miércoles")
    thursday_open = models.BooleanField(default=True, verbose_name="Jueves")
    friday_open = models.BooleanField(default=True, verbose_name="Viernes")
    saturday_open = models.BooleanField(default=True, verbose_name="Sábado")
    sunday_open = models.BooleanField(default=False, verbose_name="Domingo")

    def __str__(self):
        return f"Horario de {self.salon.name}"
"""

# --- 2. CONTENIDO CORRECTO DE FORMULARIOS (FORMS.PY) ---
CONTENIDO_FORMS = """from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee

User = get_user_model()

class OwnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Crea una contraseña segura'
    }), label="Contraseña")
    
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Repite la contraseña'
    }), label="Confirmar Contraseña")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@email.com'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario para iniciar sesión'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'address', 'phone', 'whatsapp', 'instagram']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Estética Divina'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Calle 123 # 45-67, Bogotá'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono fijo o celular'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+57 300 123 4567'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'tu_usuario_instagram'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corte de Cabello'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles del servicio...'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutos (Ej: 30)'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio (Ej: 25000)'}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
"""

# --- 3. CONTENIDO ADMIN (ADMIN.PY) ---
# Esto ayuda a que puedas ver los modelos en el panel de admin de Django si lo necesitas
CONTENIDO_ADMIN = """from django.contrib import admin
from .models import Salon, Service, Employee, SalonSchedule

admin.site.register(Salon)
admin.site.register(Service)
admin.site.register(Employee)
admin.site.register(SalonSchedule)
"""

def hacer_backup(ruta):
    if os.path.exists(ruta):
        backup_path = ruta + ".bak"
        shutil.copy2(ruta, backup_path)
        print(f"📦 Backup creado: {os.path.basename(backup_path)}")

def escribir_archivo(ruta, contenido):
    hacer_backup(ruta)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    print(f"✅ Archivo actualizado correctamente: {os.path.basename(ruta)}")

if __name__ == "__main__":
    print("🛡️ INICIANDO REPARACIÓN BLINDADA DE MODELOS 🛡️")
    print("------------------------------------------------")
    escribir_archivo(MODELS_PATH, CONTENIDO_MODELS)
    escribir_archivo(FORMS_PATH, CONTENIDO_FORMS)
    escribir_archivo(ADMIN_PATH, CONTENIDO_ADMIN)
    print("\n✨ ¡Archivos corregidos! Sigue las instrucciones para subir los cambios.")