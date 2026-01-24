from django import forms
from .models import Service, Salon, EmployeeSchedule
from apps.core.models import User
from datetime import time

def get_time_choices():
    choices = []
    for h in range(0, 24):
        for m in (0, 30):
            t = time(h, m)
            label = t.strftime('%I:%M %p')
            val = t.strftime('%H:%M')
            choices.append((val, label))
    return choices

TIME_CHOICES = get_time_choices()

COLOMBIA_CITIES = [
    ('Bogotá D.C.', 'Bogotá D.C.'), ('Medellín', 'Medellín'), ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'), ('Cartagena', 'Cartagena'), ('Bucaramanga', 'Bucaramanga'),
    ('Manizales', 'Manizales'), ('Pereira', 'Pereira'), ('Cúcuta', 'Cúcuta'),
    ('Ibagué', 'Ibagué'), ('Santa Marta', 'Santa Marta'), ('Villavicencio', 'Villavicencio'),
]

# --- FORMULARIO DE REGISTRO ---
class OwnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirmar Contraseña")
    
    # Campos para el Salón
    salon_name = forms.CharField(max_length=200, label="Nombre del Negocio")
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

# --- FORMULARIO ACTUALIZACIÓN DE NEGOCIO ---
class SalonUpdateForm(forms.ModelForm):
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad")
    class Meta:
        model = Salon
        fields = ['name', 'city', 'address', 'description', 'opening_time', 'closing_time', 'instagram_url', 'google_maps_url', 'bank_name', 'account_number']
        widgets = {
            'opening_time': forms.Select(choices=TIME_CHOICES),
            'closing_time': forms.Select(choices=TIME_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- FORMULARIO ACTUALIZACIÓN DE DUEÑO ---
class OwnerUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- HORARIOS DE EMPLEADO (CORREGIDO) ---
class EmployeeScheduleUpdateForm(forms.ModelForm):
    work_start = forms.ChoiceField(choices=TIME_CHOICES, label="Inicio Jornada")
    work_end = forms.ChoiceField(choices=TIME_CHOICES, label="Fin Jornada")
    
    # AGREGADOS: Campos de Almuerzo para que el horario funcione bien
    lunch_start = forms.ChoiceField(choices=TIME_CHOICES, label="Inicio Almuerzo")
    lunch_end = forms.ChoiceField(choices=TIME_CHOICES, label="Fin Almuerzo")

    active_days = forms.MultipleChoiceField(
        choices=[(str(i), d) for i, d in enumerate(['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'])], 
        widget=forms.CheckboxSelectMultiple,
        label="Días Laborales"
    )

    class Meta:
        model = EmployeeSchedule
        fields = ['work_start', 'work_end', 'lunch_start', 'lunch_end', 'active_days']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.active_days:
            self.initial['active_days'] = self.instance.active_days.split(',')
        
        for name, field in self.fields.items():
            # CORRECCIÓN: Si es Checkbox NO le ponemos 'appearance-none' para que se vea
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'
            else:
                # Estilo específico para que los checkboxes se vean bien
                field.widget.attrs['class'] = 'h-4 w-4 text-black border-gray-300 rounded focus:ring-black'

    def clean_active_days(self):
        return ','.join(self.cleaned_data.get('active_days', []))

# --- FORMULARIO DE SERVICIOS (CORREGIDO) ---
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        # AGREGADO: 'deposit_amount' para que aparezca el cuadro de abono
        fields = ['name', 'duration_minutes', 'price', 'deposit_amount']
        labels = {
            'name': 'Nombre del Servicio',
            'duration_minutes': 'Duración (minutos)',
            'price': 'Precio Total',
            'deposit_amount': 'Valor del Abono (Reserva)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- FORMULARIO CREACIÓN DE EMPLEADO ---
class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- FORMULARIO HORARIO GENERAL DEL SALÓN (SETTINGS) ---
class SalonScheduleForm(forms.ModelForm):
    active_days = forms.MultipleChoiceField(
        choices=[(str(i), d) for i, d in enumerate(['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'])], 
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Días que abre el negocio"
    )

    class Meta:
        model = Salon
        fields = ['opening_time', 'closing_time', 'active_days', 'deposit_percentage']
        widgets = {
            'opening_time': forms.Select(choices=TIME_CHOICES),
            'closing_time': forms.Select(choices=TIME_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.active_days:
            self.initial['active_days'] = self.instance.active_days.split(',')
            
        for name, field in self.fields.items():
            # CORRECCIÓN: Evitar ocultar los checkboxes del salón también
            if name != 'active_days':
                field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'
            else:
                 field.widget.attrs['class'] = 'h-4 w-4 text-black border-gray-300 rounded focus:ring-black'

    def clean_active_days(self):
        return ','.join(self.cleaned_data.get('active_days', []))