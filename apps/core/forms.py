from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

# Lista simplificada para el MVP (Luego cargaremos las 1101 via JSON)
CIUDADES_COLOMBIA = [
    ('', 'Selecciona tu Ciudad...'),
    ('Bogotá', 'Bogotá D.C.'),
    ('Medellín', 'Medellín'),
    ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'),
    ('Cartagena', 'Cartagena'),
    ('Bucaramanga', 'Bucaramanga'),
    ('Tunja', 'Tunja'),
    ('Sogamoso', 'Sogamoso'),
    ('Duitama', 'Duitama'),
    ('Pereira', 'Pereira'),
    ('Manizales', 'Manizales'),
]

class OwnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Crea una contraseña segura'
    }), label="Contraseña")
    
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Repite la contraseña'
    }), label="Confirmar Contraseña")

    city = forms.ChoiceField(choices=CIUDADES_COLOMBIA, widget=forms.Select(attrs={
        'class': 'form-select'
    }), label="Ciudad de Operación")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'city', 'instagram_link']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tu Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tu Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'correo@ejemplo.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '300 123 4567'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://instagram.com/tu_negocio'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.username = self.cleaned_data["email"] # Usamos email como usuario
        user.role = User.Role.OWNER # Asignación automática de Rol
        if commit:
            user.save()
        return user
