from django import forms
from .models import Service, Salon
from apps.core.models import User

# Lista de ciudades para mantener la consistencia
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

# --- HORARIOS ---
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