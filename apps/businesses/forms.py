from django import forms
from django.contrib.auth.forms import AuthenticationForm

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))

class OwnerRegistrationForm(forms.Form):
    CIUDADES_COLOMBIA = [
        ('', 'Selecciona tu Ciudad...'),
        ('Bogotá', 'Bogotá'),
        ('Medellín', 'Medellín'),
        ('Cali', 'Cali'),
        ('Barranquilla', 'Barranquilla'),
        ('Cartagena', 'Cartagena'),
        ('Tunja', 'Tunja'),
        ('Bucaramanga', 'Bucaramanga'),
        ('Pereira', 'Pereira'),
        ('Manizales', 'Manizales'),
        ('Cúcuta', 'Cúcuta'),
        ('Ibagué', 'Ibagué'),
        ('Santa Marta', 'Santa Marta'),
        ('Villavicencio', 'Villavicencio'),
        ('Pasto', 'Pasto'),
        ('Montería', 'Montería'),
        ('Neiva', 'Neiva'),
        ('Armenia', 'Armenia'),
        ('Popayán', 'Popayán'),
        ('Valledupar', 'Valledupar'),
        ('Sincelejo', 'Sincelejo'),
        ('Sogamoso', 'Sogamoso'),
        ('Duitama', 'Duitama'),
        ('Otra', 'Otra Ciudad'),
    ]

    # Datos Personales
    first_name = forms.CharField(
        label="Tu Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pablo'})
    )
    last_name = forms.CharField(
        label="Tu Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Sierra'})
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tuemail@ejemplo.com'})
    )
    password = forms.CharField(
        label="Contraseña Segura",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '******'})
    )

    # Datos del Negocio
    nombre_negocio = forms.CharField(
        label="Nombre del Negocio",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Barbería El Imperio'})
    )
    ciudad = forms.ChoiceField(
        label="Ciudad",
        choices=CIUDADES_COLOMBIA,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    direccion = forms.CharField(
        label="Dirección del Local",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cra 10 # 20-30, Centro'})
    )
    whatsapp = forms.CharField(
        label="WhatsApp del Negocio (Sin símbolos)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 573220317702'})
    )
    instagram = forms.CharField(
        label="Usuario de Instagram (Opcional)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: pasotunja'})
    )