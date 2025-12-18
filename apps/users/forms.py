from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # ¡OJO! Si 'role' no está en esta lista, NO SE GUARDA.
        fields = ('email', 'username', 'role') 
        
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@email.com', 'required': 'true'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario único'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['role'].label = "Selecciona tu perfil"
        
    def save(self, commit=True):
        user = super().save(commit=False)
        # Forzamos el guardado del email en minúsculas
        user.email = self.cleaned_data['email'].lower()
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'role', 'phone')