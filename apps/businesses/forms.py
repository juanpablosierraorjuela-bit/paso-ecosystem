from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Service, Employee, Salon, OpeningHours, User

# --- LOGIN & REGISTRO (Ya existentes, los mantenemos) ---
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

    # Horario básico para inicializar
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