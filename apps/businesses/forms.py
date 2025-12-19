from django import forms
from .models import Salon, OpeningHours, Booking, Employee, EmployeeSchedule, Service

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'description', 'city', 'address', 'phone', 'logo', 'banner', 'instagram', 'facebook', 'tiktok']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class OpeningHoursForm(forms.ModelForm):
    class Meta:
        model = OpeningHours
        fields = ['weekday', 'from_hour', 'to_hour', 'is_closed']
        widgets = {
            'from_hour': forms.TimeInput(attrs={'type': 'time'}),
            'to_hour': forms.TimeInput(attrs={'type': 'time'}),
            'weekday': forms.HiddenInput(),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['employee', 'customer_name', 'customer_phone', 'start_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)
        if service:
            # Filtrar empleados que realizan este servicio (por ahora todos los del salón)
            self.fields['employee'].queryset = Employee.objects.filter(salon=service.salon)

class EmployeeCreationForm(forms.Form):
    name = forms.CharField(label="Nombre Completo", max_length=100)
    email = forms.EmailField(label="Correo Electrónico")
    phone = forms.CharField(label="Teléfono", max_length=20)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

class EmployeeSettingsForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'phone', 'lunch_start', 'lunch_end']
        widgets = {
            'lunch_start': forms.TimeInput(attrs={'type': 'time'}),
            'lunch_end': forms.TimeInput(attrs={'type': 'time'}),
        }

class EmployeeScheduleForm(forms.ModelForm):
    class Meta:
        model = EmployeeSchedule
        fields = ['weekday', 'from_hour', 'to_hour', 'is_closed']
        widgets = {
            'from_hour': forms.TimeInput(attrs={'type': 'time'}),
            'to_hour': forms.TimeInput(attrs={'type': 'time'}),
            'weekday': forms.HiddenInput(),
        }

# --- FORMULARIO DE SERVICIOS NUEVO ---
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }