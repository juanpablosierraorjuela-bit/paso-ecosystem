from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    # Opciones de Rol
    ROLE_CHOICES = [
        ('CUSTOMER', 'Soy Cliente (Quiero reservar citas) 👤'),
        ('ADMIN', 'Soy Dueño (Tengo un negocio) 💼'),
        ('EMPLOYEE', 'Soy Colaborador (Trabajo en un salón) ✂️'),
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        label="¿Cuál es tu perfil?",
        widget=forms.RadioSelect(attrs={'class': 'list-unstyled gap-2 mb-3'}),
        help_text="Selecciona 'Colaborador' si tienes una invitación."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'role')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario único'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu Apellido'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Celular / WhatsApp'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user