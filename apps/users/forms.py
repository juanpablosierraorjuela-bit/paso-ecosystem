from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # ¡AQUÍ ESTÁ LA CLAVE! Agregamos 'role' para que se guarde lo que el usuario elige
        fields = ('email', 'username', 'role') 
        
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'nombre@ejemplo.com'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario único'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacemos que el Email sea obligatorio
        self.fields['email'].required = True
        self.fields['role'].label = "¿Cómo quieres usar PASO?"

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'role')