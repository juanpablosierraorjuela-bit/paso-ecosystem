import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Contenido para apps/core/forms.py
content = """
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
"""

# Escribir el archivo
file_path = BASE_DIR / 'apps' / 'core' / 'forms.py'

try:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print("✅ REPARACIÓN EXITOSA: apps/core/forms.py ha sido creado.")
    print("👉 Ahora puedes ejecutar 'python manage.py makemigrations' sin problemas.")
except Exception as e:
    print(f"❌ Error creando el archivo: {e}")