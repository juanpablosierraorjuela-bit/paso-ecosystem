from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class OwnerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Correo electrónico obligatorio")
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone', 'city')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'OWNER'  # Forzamos el rol de Dueño automáticamente
        if commit:
            user.save()
        return user