from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, EmployeeSchedule

User = get_user_model()

# Lista de ciudades inyectada
CIUDADES_CHOICES = [('Arauca', 'Arauca'), ('Armenia', 'Armenia'), ('Barranquilla', 'Barranquilla'), ('Bogotá', 'Bogotá'), ('Bucaramanga', 'Bucaramanga'), ('Cali', 'Cali'), ('Cartagena', 'Cartagena'), ('Cúcuta', 'Cúcuta'), ('Florencia', 'Florencia'), ('Ibagué', 'Ibagué'), ('Leticia', 'Leticia'), ('Manizales', 'Manizales'), ('Medellín', 'Medellín'), ('Mitú', 'Mitú'), ('Mocoa', 'Mocoa'), ('Montería', 'Montería'), ('Neiva', 'Neiva'), ('Pasto', 'Pasto'), ('Pereira', 'Pereira'), ('Popayán', 'Popayán'), ('Puerto Carreño', 'Puerto Carreño'), ('Inírida', 'Inírida'), ('Quibdó', 'Quibdó'), ('Riohacha', 'Riohacha'), ('San Andrés', 'San Andrés'), ('San José del Guaviare', 'San José del Guaviare'), ('Santa Marta', 'Santa Marta'), ('Sincelejo', 'Sincelejo'), ('Tunja', 'Tunja'), ('Valledupar', 'Valledupar'), ('Villavicencio', 'Villavicencio'), ('Yopal', 'Yopal'), ('Duitama', 'Duitama'), ('Sogamoso', 'Sogamoso'), ('Paipa', 'Paipa'), ('Bello', 'Bello'), ('Soacha', 'Soacha'), ('Soledad', 'Soledad')]

class SalonIntegrationsForm(forms.ModelForm):
    # Campo de ciudad personalizado con Selector
    city = forms.ChoiceField(
        choices=[('', 'Selecciona tu ciudad...')] + CIUDADES_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Ciudad"
    )

    class Meta:
        model = Salon
        fields = ['address', 'city', 'opening_time', 'closing_time', 'instagram_url', 'whatsapp_number']
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cra 10 # 20-30'}),
            'instagram_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: https://instagram.com/tu_salon'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 573001234567'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        # CORRECCIÓN: Usamos los nombres reales del modelo
        fields = ['name', 'price', 'duration_minutes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutos'}),
        }

class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono (Usuario)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = EmployeeSchedule
        fields = ['weekday', 'from_hour', 'to_hour', 'is_active']
        widgets = {
            'from_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'to_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
