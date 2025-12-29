import os

print("🚑 Restaurando campos perdidos en el Panel de Dueño...")

# Lista de ciudades (Mantenemos la mejora del selector)
CIUDADES_COLOMBIA = [
    ('Arauca', 'Arauca'), ('Armenia', 'Armenia'), ('Barranquilla', 'Barranquilla'), 
    ('Bogotá', 'Bogotá'), ('Bucaramanga', 'Bucaramanga'), ('Cali', 'Cali'), 
    ('Cartagena', 'Cartagena'), ('Cúcuta', 'Cúcuta'), ('Florencia', 'Florencia'), 
    ('Ibagué', 'Ibagué'), ('Leticia', 'Leticia'), ('Manizales', 'Manizales'), 
    ('Medellín', 'Medellín'), ('Mitú', 'Mitú'), ('Mocoa', 'Mocoa'), 
    ('Montería', 'Montería'), ('Neiva', 'Neiva'), ('Pasto', 'Pasto'), 
    ('Pereira', 'Pereira'), ('Popayán', 'Popayán'), ('Puerto Carreño', 'Puerto Carreño'), 
    ('Inírida', 'Inírida'), ('Quibdó', 'Quibdó'), ('Riohacha', 'Riohacha'), 
    ('San Andrés', 'San Andrés'), ('San José del Guaviare', 'San José del Guaviare'), 
    ('Santa Marta', 'Santa Marta'), ('Sincelejo', 'Sincelejo'), ('Tunja', 'Tunja'), 
    ('Valledupar', 'Valledupar'), ('Villavicencio', 'Villavicencio'), ('Yopal', 'Yopal'),
    ('Duitama', 'Duitama'), ('Sogamoso', 'Sogamoso'), ('Paipa', 'Paipa'), 
    ('Bello', 'Bello'), ('Soacha', 'Soacha'), ('Soledad', 'Soledad')
]

forms_path = os.path.join('apps', 'businesses', 'forms.py')

# Contenido COMPLETO y CORRECTO de forms.py
forms_content = f"""from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, EmployeeSchedule

User = get_user_model()

# Lista de ciudades inyectada
CIUDADES_CHOICES = {CIUDADES_COLOMBIA}

class SalonIntegrationsForm(forms.ModelForm):
    # Campo de ciudad con Selector
    city = forms.ChoiceField(
        choices=[('', 'Selecciona tu ciudad...')] + CIUDADES_CHOICES,
        widget=forms.Select(attrs={{'class': 'form-select'}}),
        label="Ciudad"
    )

    class Meta:
        model = Salon
        # ¡AQUÍ ESTÁ LA CORRECCIÓN! Agregamos 'name' y el resto de campos que faltaban
        fields = [
            'name', 'address', 'city', 'opening_time', 'closing_time', 
            'deposit_percentage', 'telegram_bot_token', 'telegram_chat_id', 
            'bold_identity_key', 'bold_secret_key', 'instagram_url', 'whatsapp_number'
        ]
        
        widgets = {{
            'name': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Nombre de tu negocio'}}),
            'address': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Ej: Cra 10 # 20-30'}}),
            'opening_time': forms.TimeInput(attrs={{'type': 'time', 'class': 'form-control'}}),
            'closing_time': forms.TimeInput(attrs={{'type': 'time', 'class': 'form-control'}}),
            'deposit_percentage': forms.NumberInput(attrs={{'class': 'form-control', 'placeholder': 'Ej: 50'}}),
            
            # Redes
            'instagram_url': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Ej: https://instagram.com/tu_salon'}}),
            'whatsapp_number': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Ej: 573001234567'}}),

            # Integraciones (Telegram/Bold)
            'telegram_bot_token': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Token del Bot'}}),
            'telegram_chat_id': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'ID del Chat'}}),
            'bold_identity_key': forms.PasswordInput(attrs={{'class': 'form-control', 'placeholder': 'Identity Key', 'autocomplete': 'new-password'}}, render_value=True),
            'bold_secret_key': forms.PasswordInput(attrs={{'class': 'form-control', 'placeholder': 'Secret Key', 'autocomplete': 'new-password'}}, render_value=True),
        }}

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        # Campos correctos según tu base de datos
        fields = ['name', 'price', 'duration_minutes']
        widgets = {{
            'name': forms.TextInput(attrs={{'class': 'form-control'}}),
            'price': forms.NumberInput(attrs={{'class': 'form-control'}}),
            'duration_minutes': forms.NumberInput(attrs={{'class': 'form-control', 'placeholder': 'Minutos'}}),
        }}

class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={{'class': 'form-control'}}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        widgets = {{
            'first_name': forms.TextInput(attrs={{'class': 'form-control'}}),
            'last_name': forms.TextInput(attrs={{'class': 'form-control'}}),
            'username': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Teléfono (Usuario)'}}),
            'email': forms.EmailInput(attrs={{'class': 'form-control'}}),
        }}

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = EmployeeSchedule
        fields = ['weekday', 'from_hour', 'to_hour', 'is_active']
        widgets = {{
            'from_hour': forms.TimeInput(attrs={{'type': 'time', 'class': 'form-control'}}),
            'to_hour': forms.TimeInput(attrs={{'type': 'time', 'class': 'form-control'}}),
            'is_active': forms.CheckboxInput(attrs={{'class': 'form-check-input'}}),
        }}
"""

try:
    with open(forms_path, 'w', encoding='utf-8') as f:
        f.write(forms_content)
    print("✅ ¡Formulario reparado! El campo 'Nombre' y las llaves de Bold han vuelto.")
except Exception as e:
    print(f"❌ Error escribiendo forms.py: {e}")