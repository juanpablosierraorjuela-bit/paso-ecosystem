from django import forms
from django.contrib.auth import get_user_model
from .utils.colombia_data import COLOMBIA_CITIES

User = get_user_model()

class OwnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Contraseña segura'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Confirmar contraseña'
    }))
    
    # Campos del Negocio (Se guardarán en BusinessProfile después)
    business_name = forms.CharField(
        label="Nombre del Negocio",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Barbería Vikingos'})
    )
    address = forms.CharField(
        label="Dirección",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle 123 # 45-67'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'city']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario único'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '300 123 4567'}),
            'city': forms.Select(choices=COLOMBIA_CITIES, attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
