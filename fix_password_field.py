import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ==========================================
# CONTENIDO CORREGIDO DE FORMS.PY
# ==========================================
forms_content = """
from django import forms
from .models import Service, Salon, EmployeeSchedule
from apps.core.models import User

# Lista de ciudades
COLOMBIA_CITIES = [
    ('Bogotá D.C.', 'Bogotá D.C.'), ('Medellín', 'Medellín'), ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'), ('Cartagena', 'Cartagena'), ('Bucaramanga', 'Bucaramanga'),
    ('Manizales', 'Manizales'), ('Pereira', 'Pereira'), ('Cúcuta', 'Cúcuta'),
    ('Ibagué', 'Ibagué'), ('Santa Marta', 'Santa Marta'), ('Villavicencio', 'Villavicencio'),
    ('Pasto', 'Pasto'), ('Tunja', 'Tunja'), ('Montería', 'Montería'),
    ('Valledupar', 'Valledupar'), ('Armenia', 'Armenia'), ('Neiva', 'Neiva'),
    ('Popayán', 'Popayán'), ('Sincelejo', 'Sincelejo'), ('Riohacha', 'Riohacha'),
    ('Zipaquirá', 'Zipaquirá'), ('Soacha', 'Soacha'), ('Envigado', 'Envigado'),
    ('Itagüí', 'Itagüí'), ('Bello', 'Bello'), ('Otro', 'Otro (Escribir en dirección)'),
]

# --- REGISTRO DE DUEÑO ---
class OwnerRegistrationForm(forms.ModelForm):
    # Campos del Negocio
    salon_name = forms.CharField(label="Nombre del Negocio", required=True)
    salon_address = forms.CharField(label="Dirección del Local", required=True)
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad", required=True)
    phone = forms.CharField(label="WhatsApp (Soporte)", required=True)
    
    # IMPORTANTE: Definimos la contraseña explícitamente para asegurar que se renderice
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(),
        required=True
    )
    
    # Campos Opcionales
    instagram_url = forms.URLField(label="Link Instagram", required=False)
    google_maps_url = forms.URLField(label="Link Google Maps", required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = 'OWNER'
        user.phone = self.cleaned_data["phone"]
        user.city = self.cleaned_data["city"]
        
        if commit:
            user.save()
            Salon.objects.create(
                owner=user,
                name=self.cleaned_data["salon_name"],
                address=self.cleaned_data["salon_address"],
                city=self.cleaned_data["city"],
                instagram_url=self.cleaned_data.get("instagram_url", ""),
                google_maps_url=self.cleaned_data.get("google_maps_url", ""),
                opening_time="08:00",
                closing_time="20:00"
            )
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-black focus:border-black sm:text-sm'


# --- ACTUALIZAR DATOS DUEÑO ---
class OwnerUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'phone': 'WhatsApp Personal',
            'email': 'Correo Electrónico'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- ACTUALIZAR DATOS NEGOCIO ---
class SalonUpdateForm(forms.ModelForm):
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad Base")

    class Meta:
        model = Salon
        fields = ['name', 'address', 'city', 'instagram_url', 'google_maps_url']
        labels = {
            'name': 'Nombre del Negocio',
            'address': 'Dirección Física',
            'instagram_url': 'Link Instagram',
            'google_maps_url': 'Link Google Maps'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'
            
# --- SERVICIOS ---
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'duration_minutes', 'price', 'buffer_time']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- EMPLEADOS ---
class EmployeeCreationForm(forms.ModelForm):
    username = forms.CharField(label="Usuario de Acceso", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña", required=True)
    first_name = forms.CharField(label="Nombre", required=True)
    last_name = forms.CharField(label="Apellido", required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- HORARIOS SALÓN ---
class SalonScheduleForm(forms.ModelForm):
    opening_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Apertura")
    closing_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Cierre")

    class Meta:
        model = Salon
        fields = ['opening_time', 'closing_time', 'deposit_percentage']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- HORARIO DEL EMPLEADO ---
class EmployeeScheduleUpdateForm(forms.ModelForm):
    work_start = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Inicio de Turno")
    work_end = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Fin de Turno")
    lunch_start = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Inicio Almuerzo")
    lunch_end = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Fin Almuerzo")
    
    # Días laborales
    DAYS_CHOICES = [
        ('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miércoles'), 
        ('3', 'Jueves'), ('4', 'Viernes'), ('5', 'Sábado'), ('6', 'Domingo')
    ]
    active_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES, 
        widget=forms.CheckboxSelectMultiple,
        label="Días Laborales"
    )

    class Meta:
        model = EmployeeSchedule
        fields = ['work_start', 'work_end', 'lunch_start', 'lunch_end', 'active_days']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Checkboxes pre-llenados
        if self.instance and self.instance.pk and self.instance.active_days:
            self.initial['active_days'] = self.instance.active_days.split(',')

    def clean_active_days(self):
        days = self.cleaned_data['active_days']
        return ','.join(days)
"""

def apply_fix():
    print("🔧 REPARANDO CAMPO PASSWORD EN REGISTRO DE DUEÑO...")
    with open(BASE_DIR / 'apps' / 'businesses' / 'forms.py', 'w', encoding='utf-8') as f:
        f.write(forms_content.strip())
    print("✅ apps/businesses/forms.py: Campo 'password' definido explícitamente.")

if __name__ == "__main__":
    apply_fix()