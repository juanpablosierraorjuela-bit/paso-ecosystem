from django import forms
from django.db import transaction
from .models import Service, Salon, EmployeeSchedule
from apps.core.models import User
from datetime import time

# --- CONFIGURACIONES GLOBALES ---

def get_time_choices():
    """
    Genera opciones de tiempo en formato STRING para compatibilidad con HTML y Reservas.
    Devuelve tuplas: ('08:00', '08:00 AM')
    """
    choices = []
    for h in range(0, 24):
        for m in (0, 30):
            t = time(h, m)
            # Valor: STRING 'HH:MM' (Esto arregla el error 500 y valida el HTML)
            # Etiqueta: STRING 'HH:MM AM/PM' (Legible para humanos)
            val = t.strftime('%H:%M')
            label = t.strftime('%I:%M %p')
            choices.append((val, label))
    return choices

TIME_CHOICES = get_time_choices()

DAYS_CHOICES = [
    ('0', 'Lunes'), ('1', 'Martes'), ('2', 'Miércoles'), 
    ('3', 'Jueves'), ('4', 'Viernes'), ('5', 'Sábado'), ('6', 'Domingo')
]

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

# --- MIXIN PARA ESTILOS TAILWIND ---
class TailwindMixin:
    """Aplica clases de Tailwind a todos los campos automáticamente"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                existing_classes = field.widget.attrs.get('class', '')
                new_class = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-black focus:border-black sm:text-sm'
                field.widget.attrs['class'] = f"{new_class} {existing_classes}".strip()

# --- FORMULARIOS ---

class OwnerRegistrationForm(TailwindMixin, forms.ModelForm):
    salon_name = forms.CharField(label="Nombre del Negocio", required=True)
    salon_address = forms.CharField(label="Dirección del Local", required=True)
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad", required=True)
    phone = forms.CharField(label="WhatsApp (Soporte)", required=True)
    password1 = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'placeholder': '********'}), required=True)
    password2 = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput(attrs={'placeholder': '********'}), required=True)
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

    @transaction.atomic
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
                opening_time=time(8, 0),
                closing_time=time(20, 0)
            )
        return user

class SalonScheduleForm(TailwindMixin, forms.ModelForm):
    opening_time = forms.ChoiceField(choices=TIME_CHOICES, label="Apertura")
    closing_time = forms.ChoiceField(choices=TIME_CHOICES, label="Cierre")
    active_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES, 
        widget=forms.CheckboxSelectMultiple,
        label="Días de Apertura"
    )

    class Meta:
        model = Salon
        fields = ['opening_time', 'closing_time', 'active_days', 'deposit_percentage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # CORRECCIÓN VITAL: Convertir objetos Time de la BD a Strings 'HH:MM'
            # para que el formulario HTML reconozca cuál opción está seleccionada.
            if self.instance.opening_time:
                self.initial['opening_time'] = self.instance.opening_time.strftime('%H:%M')
            if self.instance.closing_time:
                self.initial['closing_time'] = self.instance.closing_time.strftime('%H:%M')
            
            if self.instance.active_days:
                self.initial['active_days'] = self.instance.active_days.split(',')

    def clean_active_days(self):
        return ','.join(self.cleaned_data.get('active_days', []))

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class EmployeeScheduleUpdateForm(TailwindMixin, forms.ModelForm):
    work_start = forms.ChoiceField(choices=TIME_CHOICES, label="Inicio de Turno")
    work_end = forms.ChoiceField(choices=TIME_CHOICES, label="Fin de Turno")
    lunch_start = forms.ChoiceField(choices=TIME_CHOICES, label="Inicio Almuerzo")
    lunch_end = forms.ChoiceField(choices=TIME_CHOICES, label="Fin Almuerzo")
    active_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES, 
        widget=forms.CheckboxSelectMultiple,
        label="Días Laborales"
    )

    class Meta:
        model = EmployeeSchedule
        fields = ['work_start', 'work_end', 'lunch_start', 'lunch_end', 'active_days']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # CORRECCIÓN VITAL: Convertir objetos Time de la BD a Strings 'HH:MM'
            for field in ['work_start', 'work_end', 'lunch_start', 'lunch_end']:
                val = getattr(self.instance, field)
                if val:
                    self.initial[field] = val.strftime('%H:%M')
            
            if self.instance.active_days:
                self.initial['active_days'] = self.instance.active_days.split(',')

    def clean_active_days(self):
        return ','.join(self.cleaned_data.get('active_days', []))

class EmployeeCreationForm(TailwindMixin, forms.ModelForm):
    username = forms.CharField(label="Usuario de Acceso")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'phone']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"]) # ¡Vital para que funcione el login!
        if commit:
            user.save()
        return user

class ServiceForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'duration_minutes', 'price', 'buffer_time']

class OwnerUpdateForm(TailwindMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']

class SalonUpdateForm(TailwindMixin, forms.ModelForm):
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad Base")
    class Meta:
        model = Salon
        fields = ['name', 'address', 'city', 'instagram_url', 'google_maps_url', 'bank_name', 'account_number']