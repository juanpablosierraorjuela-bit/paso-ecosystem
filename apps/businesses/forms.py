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
    
    salon_name = forms.CharField(max_length=150, label="Nombre del Salón")
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad")
    address = forms.CharField(max_length=255, label="Dirección")

    class Meta:
        model = User
        fields = ['first_name', 'email', 'phone']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return cleaned_data

# --- FORMULARIO DE SERVICIOS ---
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration_minutes', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- FORMULARIO PERFIL DEL SALÓN (INFORMACIÓN GENERAL) ---
class SalonUpdateForm(forms.ModelForm):
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad")
    
    class Meta:
        model = Salon
        # Se eliminan opening_time y closing_time de aquí para evitar conflictos con el otro formulario
        fields = [
            'name', 'city', 'address', 'description', 
            'instagram_url', 'google_maps_url', 
            'bank_name', 'account_number'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

# --- FORMULARIO HORARIO GENERAL DEL SALÓN (SETTINGS) ---
class SalonScheduleForm(forms.ModelForm):
    active_days = forms.MultipleChoiceField(
        choices=[(str(i), d) for i, d in enumerate(['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'])], 
        widget=forms.CheckboxSelectMultiple,
        required=False
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
        
        # Corrección: Asegurar que el Select reconozca la hora guardada en la DB
        if self.instance.pk:
            if self.instance.opening_time:
                self.initial['opening_time'] = self.instance.opening_time.strftime('%H:%M')
            if self.instance.closing_time:
                self.initial['closing_time'] = self.instance.closing_time.strftime('%H:%M')
            
            if self.instance.active_days:
                self.initial['active_days'] = self.instance.active_days.split(',')
            
        for field_name, field in self.fields.items():
            if field_name != 'active_days':
                field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

    def clean_active_days(self):
        return ','.join(self.cleaned_data.get('active_days', []))

# --- FORMULARIO HORARIO PERSONALIZADO EMPLEADO ---
class EmployeeScheduleForm(forms.ModelForm):
    active_days = forms.MultipleChoiceField(
        choices=[(str(i), d) for i, d in enumerate(['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'])],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = EmployeeSchedule
        fields = ['work_start', 'work_end', 'lunch_start', 'lunch_end', 'active_days']
        widgets = {
            'work_start': forms.Select(choices=TIME_CHOICES),
            'work_end': forms.Select(choices=TIME_CHOICES),
            'lunch_start': forms.Select(choices=TIME_CHOICES),
            'lunch_end': forms.Select(choices=TIME_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Corrección: Asegurar que los Selects de empleados también marquen la hora actual
        if self.instance.pk:
            for time_field in ['work_start', 'work_end', 'lunch_start', 'lunch_end']:
                time_val = getattr(self.instance, time_field)
                if time_val:
                    self.initial[time_field] = time_val.strftime('%H:%M')

            if self.instance.active_days:
                self.initial['active_days'] = self.instance.active_days.split(',')

        for field_name, field in self.fields.items():
            if field_name != 'active_days':
                field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

    def clean_active_days(self):
        return ','.join(self.cleaned_data.get('active_days', []))