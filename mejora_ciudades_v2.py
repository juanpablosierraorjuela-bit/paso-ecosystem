import os
import django

# Configuración de entorno para poder acceder a la base de datos
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.businesses.models import Salon

print("🇨🇴 Iniciando Estandarización de Ciudades Colombianas (Versión Corregida)...")

# ==============================================================================
# 1. LISTA MAESTRA DE CIUDADES
# ==============================================================================
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

# ==============================================================================
# 2. ACTUALIZAR FORMS.PY (Para usar Dropdown)
# Nota: Aquí usamos doble llave {{ }} porque es un texto f-string
# ==============================================================================
forms_path = os.path.join('apps', 'businesses', 'forms.py')

forms_content = f"""from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, EmployeeSchedule

User = get_user_model()

# Lista de ciudades inyectada por el script de mejora
CIUDADES_CHOICES = {CIUDADES_COLOMBIA}

class SalonIntegrationsForm(forms.ModelForm):
    # Campo de ciudad personalizado con Selector
    city = forms.ChoiceField(
        choices=[('', 'Selecciona tu ciudad...')] + CIUDADES_CHOICES,
        widget=forms.Select(attrs={{'class': 'form-select'}}),
        label="Ciudad"
    )

    class Meta:
        model = Salon
        fields = ['address', 'city', 'opening_time', 'closing_time', 'instagram_url', 'whatsapp_number']
        widgets = {{
            'opening_time': forms.TimeInput(attrs={{'type': 'time', 'class': 'form-control'}}),
            'closing_time': forms.TimeInput(attrs={{'type': 'time', 'class': 'form-control'}}),
            'address': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Ej: Cra 10 # 20-30'}}),
            'instagram_url': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Ej: https://instagram.com/tu_salon'}}),
            'whatsapp_number': forms.TextInput(attrs={{'class': 'form-control', 'placeholder': 'Ej: 573001234567'}}),
        }}

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration']
        widgets = {{
            'name': forms.TextInput(attrs={{'class': 'form-control'}}),
            'description': forms.Textarea(attrs={{'class': 'form-control', 'rows': 3}}),
            'price': forms.NumberInput(attrs={{'class': 'form-control'}}),
            'duration': forms.NumberInput(attrs={{'class': 'form-control', 'placeholder': 'Minutos'}}),
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
    print("✅ forms.py actualizado correctamente.")
except Exception as e:
    print(f"❌ Error escribiendo forms.py: {e}")

# ==============================================================================
# 3. NORMALIZACIÓN DE DATOS EXISTENTES
# Nota: Aquí usamos llave simple { } porque es código Python real ejecutándose
# ==============================================================================
print("\n🧹 Limpiando base de datos de ciudades mal escritas...")
count = 0
salones = Salon.objects.all()

# Diccionario simple para correcciones comunes
correcciones = {
    'bogota': 'Bogotá', 'bogotá': 'Bogotá', 'BOGOTA': 'Bogotá',
    'tunja': 'Tunja', 'TUNJA': 'Tunja',
    'medellin': 'Medellín', 'medellín': 'Medellín',
    'cali': 'Cali',
    'cartagena': 'Cartagena',
    'bucaramanga': 'Bucaramanga'
}

for salon in salones:
    if salon.city:
        original = salon.city
        lower_city = original.lower().strip()
        
        # Intentamos corregir con el diccionario
        if lower_city in correcciones:
            nuevo_nombre = correcciones[lower_city]
            if original != nuevo_nombre:
                salon.city = nuevo_nombre
                salon.save()
                print(f"   ✨ Corregido: '{original}' -> '{nuevo_nombre}'")
                count += 1
        # Si no está en diccionario, intentamos Capitalizar (ej: duitama -> Duitama)
        elif not original.istitle():
            nuevo_nombre = original.title()
            salon.city = nuevo_nombre
            salon.save()
            print(f"   ✨ Formateado: '{original}' -> '{nuevo_nombre}'")
            count += 1

if count == 0:
    print("✅ Todas las ciudades ya estaban perfectas.")
else:
    print(f"✅ Se corrigieron {count} salones.")

print("\n🚀 ¡Listo! El sistema de ciudades está modernizado.")