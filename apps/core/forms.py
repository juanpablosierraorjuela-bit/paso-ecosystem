from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.core.models import User
from apps.businesses.models import Salon
from datetime import time

COLOMBIA_CITIES = [
    ('', 'Selecciona tu Ciudad...'),
    ('Bogotá D.C.', 'Bogotá D.C.'),
    ('Medellín', 'Medellín'),
    ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'),
    ('Cartagena', 'Cartagena'),
    ('Bucaramanga', 'Bucaramanga'),
    ('Manizales', 'Manizales'),
    ('Pereira', 'Pereira'),
    ('Cúcuta', 'Cúcuta'),
    ('Ibagué', 'Ibagué'),
    ('Santa Marta', 'Santa Marta'),
    ('Villavicencio', 'Villavicencio'),
    ('Pasto', 'Pasto'),
    ('Tunja', 'Tunja'),
    ('Montería', 'Montería'),
    ('Valledupar', 'Valledupar'),
    ('Armenia', 'Armenia'),
    ('Neiva', 'Neiva'),
    ('Popayán', 'Popayán'),
    ('Sincelejo', 'Sincelejo'),
    ('Riohacha', 'Riohacha'),
    ('Zipaquirá', 'Zipaquirá'),
    ('Soacha', 'Soacha'),
    ('Envigado', 'Envigado'),
    ('Itagüí', 'Itagüí'),
    ('Bello', 'Bello'),
    ('Otro', 'Otro (Escribir en dirección)'),
]

class OwnerRegistrationForm(UserCreationForm):
    # --- Datos del Dueño ---
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")
    email = forms.EmailField(required=True, label="Correo Electrónico", help_text="Recibirás tu validación aquí.")
    phone = forms.CharField(max_length=20, required=True, label="WhatsApp Personal")
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad Base")

    # --- Datos del Negocio (Salón) ---
    salon_name = forms.CharField(max_length=150, required=True, label="Nombre del Negocio")
    salon_address = forms.CharField(max_length=255, required=True, label="Dirección Física")
    
    instagram_url = forms.URLField(required=False, label="Link de Instagram (Opcional)")
    google_maps_url = forms.URLField(required=False, label="Link de Google Maps (Opcional)")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'city')

    def __init__(self, *args, **kwargs):
        super(OwnerRegistrationForm, self).__init__(*args, **kwargs)
        # ESTILO "LUXURY" AUTOMÁTICO
        # Recorremos todos los campos y les ponemos la clase de Tailwind
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'appearance-none block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-black focus:border-black sm:text-sm'
            
            # Placeholder inteligente
            if field.label:
                field.widget.attrs['placeholder'] = field.label

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'OWNER'
        user.is_verified_payment = False
        if commit:
            user.save()

        Salon.objects.create(
            owner=user,
            name=self.cleaned_data['salon_name'],
            city=self.cleaned_data['city'],
            address=self.cleaned_data['salon_address'],
            instagram_url=self.cleaned_data.get('instagram_url', ''),
            google_maps_url=self.cleaned_data.get('google_maps_url', ''),
            opening_time=time(9, 0),
            closing_time=time(20, 0),
            deposit_percentage=50
        )
        return user