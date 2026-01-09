from django import forms
from .models import Service, Salon
from apps.core.models import User

# --- FORMULARIO DE SERVICIOS ---
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'duration_minutes', 'price', 'buffer_time']
        labels = {
            'name': 'Nombre del Servicio',
            'duration_minutes': 'Duración (minutos)',
            'price': 'Precio (COP)',
            'buffer_time': 'Tiempo de Limpieza (minutos)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- FORMULARIO DE EMPLEADOS ---
class EmployeeCreationForm(forms.ModelForm):
    # Campos extra para crear el Usuario
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

# --- FORMULARIO DE HORARIO (SALÓN) ---
class SalonScheduleForm(forms.ModelForm):
    opening_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Hora de Apertura")
    closing_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Hora de Cierre")

    class Meta:
        model = Salon
        fields = ['opening_time', 'closing_time', 'deposit_percentage']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'