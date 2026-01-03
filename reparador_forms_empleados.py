import os

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FORMS_PATH = os.path.join(BASE_DIR, "apps", "businesses", "forms.py")

# --- CONTENIDO CORREGIDO DE FORMS.PY (INCLUYE EmployeeForm y EmployeeCreationForm) ---
CONTENIDO_FORMS = """from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee

User = get_user_model()

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
        fields = ['name', 'address', 'phone', 'whatsapp', 'instagram']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control'}),
        }

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

# --- EL FORMULARIO QUE FALTABA (RESTAURADO) ---
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

# --- EL NUEVO FORMULARIO DE CREACIÓN CON USUARIO ---
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
"""

def reparar_forms():
    print("🚑 Reparando forms.py...")
    with open(FORMS_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_FORMS)
    print("✅ ¡forms.py arreglado! Se han incluido todos los formularios necesarios.")

if __name__ == "__main__":
    reparar_forms()