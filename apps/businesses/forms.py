from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee, SalonSchedule

User = get_user_model()

# FORMULARIO DE USUARIO (DUEÑO)
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

# FORMULARIO DE NEGOCIO (SALÓN)
class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'address', 'city', 'phone', 'whatsapp', 'instagram']
        labels = {
            'name': 'Nombre del Negocio',
            'address': 'Dirección Física',
            'city': 'Ciudad',
            'phone': 'Teléfono',
            'whatsapp': 'Número de WhatsApp',
            'instagram': 'Usuario Instagram',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Barbería El Rey'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Calle 123 # 45-67'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bogotá'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 300 123 4567'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 300 123 4567'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: barberia_elrey (sin @)'}),
        }

# OTROS FORMULARIOS NECESARIOS PARA VIEWS.PY
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'price']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'phone', 'email']

class EmployeeCreationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'phone', 'email']

class SalonScheduleForm(forms.ModelForm):
    class Meta:
        model = SalonSchedule
        fields = ['monday_open', 'tuesday_open', 'wednesday_open', 'thursday_open', 'friday_open', 'saturday_open', 'sunday_open']
