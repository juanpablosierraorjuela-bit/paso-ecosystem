from django import forms
from django.utils import timezone
from .models import Salon, Service, OpeningHours, Booking, Employee, EmployeeSchedule

# --- FORMULARIO DE SERVICIOS (NUEVO) ---
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corte de Cabello'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Breve descripción...'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class EmployeeCreationForm(forms.Form):
    name = forms.CharField(label="Nombre Completo", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez'}))
    email = forms.EmailField(label="Correo Electrónico (Será su usuario)", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'empleado@salon.com'}))
    phone = forms.CharField(label="Teléfono", max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña de Acceso", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class SalonCreateForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = [
            'name', 'slug', 'description', 'city', 'address', 'phone', 
            'latitude', 'longitude', 
            'logo', 'banner',
            'instagram', 'facebook', 'tiktok',
            'bold_api_key', 'bold_signing_key', 
            'telegram_bot_token', 'telegram_chat_id'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre-sin-espacios'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'tiktok': forms.URLInput(attrs={'class': 'form-control'}),
            'bold_api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'bold_signing_key': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram_bot_token': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram_chat_id': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name not in ['name', 'city', 'address', 'phone']: 
                self.fields[field_name].required = False

class OpeningHoursForm(forms.ModelForm):
    class Meta:
        model = OpeningHours
        fields = ['weekday', 'from_hour', 'to_hour', 'is_closed']
        widgets = {
            'weekday': forms.Select(attrs={'class': 'form-select'}),
            'from_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'to_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'is_closed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BookingForm(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.none(),
        required=False,
        empty_label="Cualquiera (Asignación Automática)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Booking
        fields = ['employee', 'customer_name', 'customer_phone', 'start_time']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu teléfono'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)
        if service:
            self.fields['employee'].queryset = service.salon.employees.all()
    
    def clean_start_time(self):
        start_time = self.cleaned_data['start_time']
        if start_time < timezone.now():
            raise forms.ValidationError("No puedes reservar en el pasado.")
        return start_time

class EmployeeSettingsForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['lunch_start', 'lunch_end', 'bold_api_key', 'bold_signing_key', 'telegram_bot_token', 'telegram_chat_id']
        widgets = {
            'lunch_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'lunch_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'bold_api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'bold_signing_key': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram_bot_token': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram_chat_id': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EmployeeScheduleForm(forms.ModelForm):
    class Meta:
        model = EmployeeSchedule
        fields = ['weekday', 'from_hour', 'to_hour', 'is_closed']
        widgets = {
            'weekday': forms.Select(attrs={'class': 'form-select', 'disabled': 'disabled'}), 
            'from_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'to_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'is_closed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }