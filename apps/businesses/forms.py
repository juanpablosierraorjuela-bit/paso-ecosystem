
from django import forms
from django.contrib.auth import get_user_model
from .models import Salon

User = get_user_model()

# Lista de Ciudades Principales (Placeholder para el ejemplo, en prod usaríamos JSON completo)
CIUDADES_COLOMBIA = [
    ('Bogotá', 'Bogotá D.C.'), ('Medellín', 'Medellín'), ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'), ('Cartagena', 'Cartagena'), ('Tunja', 'Tunja'),
    ('Bucaramanga', 'Bucaramanga'), ('Pereira', 'Pereira'), ('Manizales', 'Manizales'),
]

class OwnerRegistrationForm(forms.ModelForm):
    # Campos de Usuario
    email = forms.EmailField(label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '******'}))
    phone = forms.CharField(label="WhatsApp Personal", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '300...'}))
    
    # Campos de Negocio
    salon_name = forms.CharField(label="Nombre del Negocio", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Barbería Vikingos'}))
    city = forms.ChoiceField(label="Ciudad", choices=CIUDADES_COLOMBIA, widget=forms.Select(attrs={'class': 'form-select'}))
    address = forms.CharField(label="Dirección", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cra 15 # 12-34'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu Apellido'}),
        }

    def save(self, commit=True):
        # 1. Crear Usuario
        user = super().save(commit=False)
        user.username = self.cleaned_data['email'] # Usamos email como usuario
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        user.role = 'OWNER'
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
            
            # 2. Crear Salón Vinculado
            Salon.objects.create(
                owner=user,
                name=self.cleaned_data['salon_name'],
                city=self.cleaned_data['city'],
                address=self.cleaned_data['address']
            )
        return user
