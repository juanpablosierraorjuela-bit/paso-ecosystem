from django import forms
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
