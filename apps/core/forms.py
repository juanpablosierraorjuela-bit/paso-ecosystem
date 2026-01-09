from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.core.models import User
from apps.businesses.models import Salon
from datetime import time

COLOMBIA_CITIES = [('', 'Selecciona tu Ciudad...'), ('Bogotá D.C.', 'Bogotá D.C.'), ('Medellín', 'Medellín'), ('Cali', 'Cali'), ('Barranquilla', 'Barranquilla'), ('Cartagena', 'Cartagena'), ('Bucaramanga', 'Bucaramanga'), ('Manizales', 'Manizales'), ('Pereira', 'Pereira'), ('Cúcuta', 'Cúcuta'), ('Ibagué', 'Ibagué'), ('Santa Marta', 'Santa Marta'), ('Villavicencio', 'Villavicencio'), ('Pasto', 'Pasto'), ('Tunja', 'Tunja'), ('Montería', 'Montería'), ('Valledupar', 'Valledupar'), ('Armenia', 'Armenia'), ('Neiva', 'Neiva'), ('Popayán', 'Popayán'), ('Sincelejo', 'Sincelejo'), ('Riohacha', 'Riohacha'), ('Tunja', 'Tunja'), ('Zipaquirá', 'Zipaquirá'), ('Soacha', 'Soacha'), ('Envigado', 'Envigado'), ('Itagüí', 'Itagüí'), ('Bello', 'Bello'), ('Otro', 'Otro (Escribir en dirección)')]

class OwnerRegistrationForm(UserCreationForm):
    # --- Datos del Dueño ---
    first_name = forms.CharField(max_length=30, required=True, label="Nombre")
    last_name = forms.CharField(max_length=30, required=True, label="Apellido")
    email = forms.EmailField(required=True, label="Correo Electrónico", help_text="Recibirás tu validación aquí.")
    phone = forms.CharField(max_length=20, required=True, label="WhatsApp Personal / Soporte")
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, label="Ciudad Base")

    # --- Datos del Negocio (Salón) ---
    salon_name = forms.CharField(max_length=150, required=True, label="Nombre del Negocio")
    salon_address = forms.CharField(max_length=255, required=True, label="Dirección Física")
    
    # --- Redes y Marketing ---
    instagram_url = forms.URLField(required=False, label="Link de Instagram (Opcional)", widget=forms.URLInput(attrs={'placeholder': 'https://instagram.com/tu_negocio'}))
    google_maps_url = forms.URLField(required=False, label="Link de Google Maps (Opcional)", widget=forms.URLInput(attrs={'placeholder': 'https://maps.google.com/...'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'city')

    def save(self, commit=True):
        # 1. Guardar el Usuario (Dueño)
        user = super().save(commit=False)
        user.role = 'OWNER'
        user.is_verified_payment = False # Empieza sin pagar
        if commit:
            user.save()

        # 2. Crear el Negocio (Salón) automáticamente
        # Se establecen horarios por defecto (9am - 8pm) que luego pueden editar
        Salon.objects.create(
            owner=user,
            name=self.cleaned_data['salon_name'],
            city=self.cleaned_data['city'],
            address=self.cleaned_data['salon_address'],
            instagram_url=self.cleaned_data.get('instagram_url', ''),
            google_maps_url=self.cleaned_data.get('google_maps_url', ''),
            opening_time=time(9, 0),  # Default apertura
            closing_time=time(20, 0), # Default cierre
            deposit_percentage=50
        )
        return user