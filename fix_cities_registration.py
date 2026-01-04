import os
import subprocess

# RUTA DE FORMS.PY
forms_path = os.path.join('apps', 'businesses', 'forms.py')
print(f" Implementando ciudades de Colombia en {forms_path}...")

new_forms_code = r"""from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee, EmployeeSchedule
from datetime import datetime

User = get_user_model()

# --- LISTA DE CIUDADES DE COLOMBIA ---
COLOMBIA_CITIES = [
    ('Bogotá', 'Bogotá'),
    ('Medellín', 'Medellín'),
    ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'),
    ('Cartagena', 'Cartagena'),
    ('Cúcuta', 'Cúcuta'),
    ('Bucaramanga', 'Bucaramanga'),
    ('Pereira', 'Pereira'),
    ('Santa Marta', 'Santa Marta'),
    ('Ibagué', 'Ibagué'),
    ('Pasto', 'Pasto'),
    ('Manizales', 'Manizales'),
    ('Neiva', 'Neiva'),
    ('Villavicencio', 'Villavicencio'),
    ('Armenia', 'Armenia'),
    ('Valledupar', 'Valledupar'),
    ('Montería', 'Montería'),
    ('Sincelejo', 'Sincelejo'),
    ('Popayán', 'Popayán'),
    ('Tunja', 'Tunja'),
    ('Riohacha', 'Riohacha'),
    ('Florencia', 'Florencia'),
    ('Quibdó', 'Quibdó'),
    ('Arauca', 'Arauca'),
    ('Yopal', 'Yopal'),
    ('Leticia', 'Leticia'),
    ('San Andrés', 'San Andrés'),
    ('Mocoa', 'Mocoa'),
    ('Mitú', 'Mitú'),
    ('Puerto Carreño', 'Puerto Carreño'),
    ('Inírida', 'Inírida'),
    ('San José del Guaviare', 'San José del Guaviare'),
    ('Sogamoso', 'Sogamoso'),
    ('Duitama', 'Duitama'),
    ('Girardot', 'Girardot'),
    ('Barrancabermeja', 'Barrancabermeja'),
    ('Buenaventura', 'Buenaventura'),
    ('Tumaco', 'Tumaco'),
    ('Ipiales', 'Ipiales'),
    ('Palmira', 'Palmira'),
    ('Tuluá', 'Tuluá'),
    ('Buga', 'Buga'),
    ('Cartago', 'Cartago'),
    ('Soacha', 'Soacha'),
    ('Bello', 'Bello'),
    ('Itagüí', 'Itagüí'),
    ('Envigado', 'Envigado'),
    ('Apartadó', 'Apartadó'),
]

# Generador de horas
TIME_CHOICES = []
for h in range(5, 23):
    for m in (0, 30):
        time_str = f"{h:02d}:{m:02d}"
        display_str = datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
        TIME_CHOICES.append((time_str, display_str))

class EmployeeScheduleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        if self.instance.pk:
            for day in days:
                db_val = getattr(self.instance, f"{day}_hours", "CERRADO")
                is_active = db_val != "CERRADO"
                self.fields[f"{day}_active"].initial = is_active
                if is_active and '-' in db_val:
                    start, end = db_val.split('-')
                    self.fields[f"{day}_start"].initial = start
                    self.fields[f"{day}_end"].initial = end

        if self.salon:
            map_salon = {
                'monday': self.salon.work_monday, 'tuesday': self.salon.work_tuesday,
                'wednesday': self.salon.work_wednesday, 'thursday': self.salon.work_thursday,
                'friday': self.salon.work_friday, 'saturday': self.salon.work_saturday,
                'sunday': self.salon.work_sunday
            }
            for day, works in map_salon.items():
                if not works:
                    self.fields[f"{day}_active"].disabled = True
                    self.fields[f"{day}_active"].help_text = "Cerrado por el negocio."
                    self.fields[f"{day}_active"].initial = False

    monday_active = forms.BooleanField(required=False, label="Lunes")
    monday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    monday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    tuesday_active = forms.BooleanField(required=False, label="Martes")
    tuesday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    tuesday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    wednesday_active = forms.BooleanField(required=False, label="Miércoles")
    wednesday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    wednesday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    thursday_active = forms.BooleanField(required=False, label="Jueves")
    thursday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    thursday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    friday_active = forms.BooleanField(required=False, label="Viernes")
    friday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    friday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    saturday_active = forms.BooleanField(required=False, label="Sábado")
    saturday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    saturday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    sunday_active = forms.BooleanField(required=False, label="Domingo")
    sunday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    sunday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)

    class Meta:
        model = EmployeeSchedule
        fields = []

    def save(self, commit=True):
        schedule = super().save(commit=False)
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            is_active = self.cleaned_data.get(f"{day}_active")
            start = self.cleaned_data.get(f"{day}_start")
            end = self.cleaned_data.get(f"{day}_end")
            if is_active and start and end:
                setattr(schedule, f"{day}_hours", f"{start}-{end}")
            else:
                setattr(schedule, f"{day}_hours", "CERRADO")
        if commit: schedule.save()
        return schedule

class SalonRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Usuario")
    email = forms.EmailField(label="Correo Electrónico")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")
    salon_name = forms.CharField(max_length=255, label="Nombre del Negocio")
    
    # CAMBIO IMPORTANTE: Ciudad como lista desplegable
    city = forms.ChoiceField(
        choices=COLOMBIA_CITIES, 
        label="Ciudad", 
        initial='Bogotá',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    address = forms.CharField(max_length=255, label="Dirección")
    phone = forms.CharField(max_length=50, label="Teléfono/WhatsApp")
    instagram_link = forms.URLField(required=False, label="Instagram (Opcional)")
    maps_link = forms.URLField(required=False, label="Google Maps (Opcional)")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2: raise forms.ValidationError("Las contraseñas no coinciden")
        return p2

class SalonSettingsForm(forms.ModelForm):
    # También actualizamos la configuración para que use la lista
    city = forms.ChoiceField(
        choices=COLOMBIA_CITIES, 
        label="Ciudad",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Salon
        fields = ['name', 'city', 'address', 'whatsapp_number', 'instagram_link', 'maps_link', 
                  'opening_time', 'closing_time', 'deposit_percentage',
                  'work_monday', 'work_tuesday', 'work_wednesday', 'work_thursday', 'work_friday', 'work_saturday', 'work_sunday']
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'price', 'buffer_time', 'is_active']

class EmployeeForm(forms.ModelForm):
    username = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    class Meta:
        model = Employee
        fields = ['name', 'phone', 'instagram_link', 'is_active']
"""

with open(forms_path, 'w', encoding='utf-8') as f:
    f.write(new_forms_code)

print(" Subiendo actualización de Ciudades a GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Feat: Lista de Ciudades Colombia y Fix Registro"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print(" ¡LISTO! Ciudades estandarizadas y registro corregido.")
except Exception as e:
    print(f" Nota de Git: {e}")

try:
    os.remove(__file__)
except:
    pass