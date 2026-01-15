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
    ('Pasto', 'Pasto'), ('Tunja', 'Tunja'), ('Montería', 'Montería'),
    ('Valledupar', 'Valledupar'), ('Armenia', 'Armenia'), ('Neiva', 'Neiva'),
    ('Popayán', 'Popayán'), ('Sincelejo', 'Sincelejo'), ('Riohacha', 'Riohacha'),
    ('Zipaquirá', 'Zipaquirá'), ('Soacha', 'Soacha'), ('Envigado', 'Envigado'),
    ('Itagüí', 'Itagüí'), ('Bello', 'Bello'), ('Otro', 'Otro (Escribir en dirección)'),
]

class OwnerRegistrationForm(forms.ModelForm):
    salon_name = forms.CharField(label="Nombre del Negocio", required=True)
    salon_address = forms.CharField(label="Dirección del Local", required=True)
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad", required=True)
    phone = forms.CharField(label="WhatsApp (Soporte)", required=True)
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'placeholder': '********', 'class': 'pr-12'}), required=True)
    password2 = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput(attrs={'placeholder': '********', 'class': 'pr-12'}), required=True)
    instagram_url = forms.URLField(label="Link Instagram", required=False)
    google_maps_url = forms.URLField(label="Link Google Maps", required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
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
        base_class = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-black focus:border-black sm:text-sm'
        for name, field in self.fields.items():
            if name in ['password1', 'password2']:
                field.widget.attrs['class'] = base_class + ' pr-12'
            else:
                field.widget.attrs['class'] = base_class

class OwnerUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

class SalonUpdateForm(forms.ModelForm):
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad Base")
    class Meta:
        model = Salon
        fields = ['name', 'address', 'city', 'instagram_url', 'google_maps_url', 'bank_name', 'account_number']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

class SalonScheduleForm(forms.ModelForm):
    opening_time = forms.ChoiceField(choices=TIME_CHOICES, label="Apertura")
    closing_time = forms.ChoiceField(choices=TIME_CHOICES, label="Cierre")
    
    DAYS_CHOICES = [
        ('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miércoles'), 
        ('3', 'Jueves'), ('4', 'Viernes'), ('5', 'Sábado'), ('6', 'Domingo')
    ]
    active_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES, 
        widget=forms.CheckboxSelectMultiple,
        label="Días de Apertura",
        required=False
    )

    class Meta:
        model = Salon
        fields = ['opening_time', 'closing_time', 'active_days', 'deposit_percentage']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.active_days:
                self.initial['active_days'] = self.instance.active_days.split(',')
            if self.instance.opening_time:
                self.initial['opening_time'] = self.instance.opening_time.strftime('%H:%M')
            if self.instance.closing_time:
                self.initial['closing_time'] = self.instance.closing_time.strftime('%H:%M')
        
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

    def clean_active_days(self):
        days = self.cleaned_data.get('active_days', [])
        return ','.join(days)

class EmployeeScheduleUpdateForm(forms.ModelForm):
    work_start = forms.ChoiceField(choices=TIME_CHOICES, label="Inicio de Turno")
    work_end = forms.ChoiceField(choices=TIME_CHOICES, label="Fin de Turno")
    lunch_start = forms.ChoiceField(choices=TIME_CHOICES, label="Inicio Almuerzo")
    lunch_end = forms.ChoiceField(choices=TIME_CHOICES, label="Fin Almuerzo")
    
    DAYS_CHOICES = [
        ('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miércoles'), 
        ('3', 'Jueves'), ('4', 'Viernes'), ('5', 'Sábado'), ('6', 'Domingo')
    ]
    active_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES, 
        widget=forms.CheckboxSelectMultiple,
        label="Días Laborales",
        required=False
    )

    class Meta:
        model = EmployeeSchedule
        fields = ['work_start', 'work_end', 'lunch_start', 'lunch_end', 'active_days']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # --- SOLUCIÓN: FILTRAR DÍAS SEGÚN EL SALÓN DEL DUEÑO ---
        try:
            # Buscamos el salón asociado al dueño que creó a este empleado
            # El dueño tiene un OTO con Salon llamado 'owned_salon'
            # Asumiendo que buscamos el salón del OWNER relacionado.
            salon = Salon.objects.filter(owner__managed_employees=self.instance.employee).first()
            if not salon:
                 # Intento alternativo según tu lógica de registro: Salon.owner == boss
                 salon = Salon.objects.filter(owner=self.instance.employee.boss).first()

            if salon and salon.active_days:
                allowed_days = salon.active_days.split(',')
                # Filtramos las opciones del checkbox para que solo aparezcan los días permitidos por el salón
                self.fields['active_days'].choices = [
                    (c[0], c[1]) for c in self.DAYS_CHOICES if c[0] in allowed_days
                ]
        except:
            pass

        if self.instance and self.instance.pk:
            if self.instance.active_days:
                self.initial['active_days'] = self.instance.active_days.split(',')
            if self.instance.work_start:
                self.initial['work_start'] = self.instance.work_start.strftime('%H:%M')
            if self.instance.work_end:
                self.initial['work_end'] = self.instance.work_end.strftime('%H:%M')
            if self.instance.lunch_start:
                self.initial['lunch_start'] = self.instance.lunch_start.strftime('%H:%M')
            if self.instance.lunch_end:
                self.initial['lunch_end'] = self.instance.lunch_end.strftime('%H:%M')
            
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

    def clean_active_days(self):
        days = self.cleaned_data.get('active_days', [])
        return ','.join(days)

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'duration_minutes', 'price', 'buffer_time']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-black focus:border-black sm:text-sm'

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