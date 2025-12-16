from django import forms
from .models import Salon, Service, OpeningHours, Booking, Employee, EmployeeSchedule

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
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Peluquería Estilo'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'identificador-unico-sin-espacios'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Tunja'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Cra 10 # 20-30'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '310 123 4567'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': '0.0'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': '0.0'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/...'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'tiktok': forms.URLInput(attrs={'class': 'form-control'}),
            'bold_api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'bold_signing_key': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram_bot_token': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram_chat_id': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Campos opcionales
        optional_fields = [
            'slug', 'latitude', 'longitude', 'logo', 'banner',
            'instagram', 'facebook', 'tiktok', 
            'bold_api_key', 'bold_signing_key', 
            'telegram_bot_token', 'telegram_chat_id'
        ]
        for field in optional_fields:
            if field in self.fields:
                self.fields[field].required = False

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'duration_minutes', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Corte de Cabello'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '30'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '25000'}),
        }

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
        label="¿Prefieres a alguien?",
        empty_label="Cualquiera (El sistema asignará al mejor)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Booking
        fields = ['employee', 'customer_name', 'customer_phone', 'start_time']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu celular'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)
        if service:
            self.fields['employee'].queryset = service.salon.employees.all()

class EmployeeSettingsForm(forms.ModelForm):
    """
    Formulario de Configuración del Empleado (COMPLETO)
    """
    class Meta:
        model = Employee
        fields = ['lunch_start', 'lunch_end', 'bold_api_key', 'bold_signing_key', 'telegram_bot_token', 'telegram_chat_id']
        widgets = {
            'lunch_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'lunch_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'bold_api_key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Identity Key'}),
            'bold_signing_key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Secret Key'}),
            'telegram_bot_token': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Token del Bot'}),
            'telegram_chat_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID de Chat'}),
        }

class EmployeeScheduleForm(forms.ModelForm):
    class Meta:
        model = EmployeeSchedule
        fields = ['weekday', 'from_hour', 'to_hour', 'is_closed']
        widgets = {
            'weekday': forms.Select(attrs={'class': 'form-select'}),
            'from_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'to_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'is_closed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }