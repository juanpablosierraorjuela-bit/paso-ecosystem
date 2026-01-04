import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
FORMS_PATH = os.path.join(APP_DIR, "forms.py")

# --- CONTENIDO PERFECTO Y LIMPIO DE FORMS.PY ---
CONTENIDO_FORMS = """from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee, SalonSchedule

User = get_user_model()

# --- 1. REGISTRO DUEÑO ---
class OwnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirmar")
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("password_confirm"):
            raise forms.ValidationError("Las contraseñas no coinciden.")

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'address', 'city', 'phone', 'whatsapp', 'instagram']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bogotá'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control'}),
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

# --- 4. CONFIGURACIÓN HORARIOS (EL NUEVO) ---
class SalonScheduleForm(forms.ModelForm):
    class Meta:
        model = SalonSchedule
        fields = ['monday_open', 'tuesday_open', 'wednesday_open', 'thursday_open', 'friday_open', 'saturday_open', 'sunday_open']
        # Aquí puedes agregar widgets si quieres checkboxes bonitos, pero por defecto funcionan
"""

def limpiar_forms():
    print("🧹 Limpiando forms.py de código viejo...")
    with open(FORMS_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_FORMS)
    print("✅ forms.py saneado. Adiós a SalonSettingsForm.")

if __name__ == "__main__":
    limpiar_forms()