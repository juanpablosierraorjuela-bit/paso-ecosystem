from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # IMPORTANTE: Aquí incluimos 'role' para que se guarde la selección
        fields = ('email', 'username', 'role')
        
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'nombre@ejemplo.com'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Elige un usuario'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['role'].label = "¿Cómo quieres usar la plataforma?"
        # Ayuda visual para el campo rol
        self.fields['role'].help_text = "Selecciona 'Dueño' si vas a registrar tu negocio."

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'role', 'phone')