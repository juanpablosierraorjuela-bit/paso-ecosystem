from django import forms
from django.contrib.auth import get_user_model
from apps.businesses.models import Salon 

User = get_user_model()

class OwnerSignupForm(forms.ModelForm):
    '''Registro exclusivo para DUEÑOS (Paso 1)'''
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Tu Nombre',
            'last_name': 'Tu Apellido',
            'email': 'Correo Electrónico'
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.ADMIN  # <--- FUERZA ROL DE DUEÑO
        if commit:
            user.save()
        return user

class ClientSignupForm(forms.ModelForm):
    '''Registro exclusivo para CLIENTES'''
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.CLIENT  # <--- FUERZA ROL DE CLIENTE
        if commit:
            user.save()
        return user

class CreateSalonForm(forms.ModelForm):
    '''
    Formulario adaptado a TU models.py
    Campos: Nombre, WhatsApp, Hora Apertura, Hora Cierre.
    '''
    class Meta:
        model = Salon
        fields = ['name', 'phone', 'opening_time', 'closing_time']
        labels = {
            'name': 'Nombre del Negocio',
            'phone': 'WhatsApp de Contacto (ej. 57300...)',
            'opening_time': 'Hora de Apertura',
            'closing_time': 'Hora de Cierre',
        }
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
