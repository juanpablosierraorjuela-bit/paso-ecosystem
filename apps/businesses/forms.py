from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from apps.core_saas.models import User
from .models import Salon, Service, Employee, EmployeeSchedule

# --- LISTA MAESTRA DE CIUDADES ---
CIUDADES_COLOMBIA = [
    ('', 'Selecciona una ciudad...'),
    ('Arauca', 'Arauca'),
    ('Armenia', 'Armenia'),
    ('Barranquilla', 'Barranquilla'),
    ('Bogotá', 'Bogotá'),
    ('Bucaramanga', 'Bucaramanga'),
    ('Cali', 'Cali'),
    ('Cartagena', 'Cartagena'),
    ('Cúcuta', 'Cúcuta'),
    ('Florencia', 'Florencia'),
    ('Ibagué', 'Ibagué'),
    ('Leticia', 'Leticia'),
    ('Manizales', 'Manizales'),
    ('Medellín', 'Medellín'),
    ('Mitú', 'Mitú'),
    ('Mocoa', 'Mocoa'),
    ('Montería', 'Montería'),
    ('Neiva', 'Neiva'),
    ('Pasto', 'Pasto'),
    ('Pereira', 'Pereira'),
    ('Popayán', 'Popayán'),
    ('Puerto Carreño', 'Puerto Carreño'),
    ('Inírida', 'Inírida'),
    ('Quibdó', 'Quibdó'),
    ('Riohacha', 'Riohacha'),
    ('San Andrés', 'San Andrés'),
    ('San José del Guaviare', 'San José del Guaviare'),
    ('Santa Marta', 'Santa Marta'),
    ('Sincelejo', 'Sincelejo'),
    ('Soacha', 'Soacha'),
    ('Sogamoso', 'Sogamoso'),
    ('Tunja', 'Tunja'),
    ('Valledupar', 'Valledupar'),
    ('Villavicencio', 'Villavicencio'),
    ('Yopal', 'Yopal'),
    ('Zipaquirá', 'Zipaquirá'),
]

class OwnerSignUpForm(UserCreationForm):
    salon_name = forms.CharField(label="Nombre del Negocio", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Barbería Supreme'}))
    
    # ¡AQUÍ ESTÁ EL DROPDOWN RECUPERADO!
    city = forms.ChoiceField(
        label="Ciudad",
        choices=CIUDADES_COLOMBIA,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    address = forms.CharField(label="Dirección", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cra 15 # 85-20'}))
    phone = forms.CharField(label="WhatsApp", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '3001234567'}))
    instagram_link = forms.URLField(label="Instagram", required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/tu_negocio'}))
    maps_link = forms.URLField(label="Maps", required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Link de Google Maps'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.role = 'OWNER'
        user.save()
        
        # Lógica +57
        raw_phone = self.cleaned_data['phone']
        clean_phone = ''.join(filter(str.isdigit, raw_phone))
        if clean_phone.startswith('3') and len(clean_phone) == 10:
            clean_phone = '57' + clean_phone

        Salon.objects.create(
            owner=user, name=self.cleaned_data['salon_name'], city=self.cleaned_data['city'],
            address=self.cleaned_data['address'], whatsapp_number=clean_phone,
            instagram_link=self.cleaned_data.get('instagram_link'), maps_link=self.cleaned_data.get('maps_link')
        )
        return user

class SalonForm(forms.ModelForm):
    # ¡DROPDOWN TAMBIÉN EN CONFIGURACIÓN!
    city = forms.ChoiceField(
        label="Ciudad",
        choices=CIUDADES_COLOMBIA,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Salon
        # Mantenemos TODOS los campos de la lógica avanzada (Horarios, Días, Abono)
        fields = ['name', 'description', 'city', 'address', 'whatsapp_number', 'instagram_link', 'maps_link', 
                  'opening_time', 'closing_time', 'work_monday', 'work_tuesday', 'work_wednesday', 
                  'work_thursday', 'work_friday', 'work_saturday', 'work_sunday', 'deposit_percentage']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-control'}),
            'maps_link': forms.URLInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'deposit_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'buffer_time', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'buffer_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class EmployeeForm(forms.ModelForm):
    username = forms.CharField(label="Usuario de Acceso", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Employee
        fields = ['name', 'phone', 'instagram_link', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        employee = super().save(commit=False)
        return employee

class EmployeeScheduleForm(forms.ModelForm):
    class Meta:
        model = EmployeeSchedule
        fields = ['monday_hours', 'tuesday_hours', 'wednesday_hours', 'thursday_hours', 'friday_hours', 'saturday_hours', 'sunday_hours']
        widgets = {
            'monday_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:00-18:00'}),
            'tuesday_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:00-18:00'}),
            'wednesday_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:00-18:00'}),
            'thursday_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:00-18:00'}),
            'friday_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:00-18:00'}),
            'saturday_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:00-18:00'}),
            'sunday_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CERRADO'}),
        }
