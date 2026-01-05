from django import forms
from .models import Service
from apps.core.models import User

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'buffer_minutes', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Corte Clásico'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Descripción para el buscador...'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Minutos'}),
            'buffer_minutes': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Tiempo de limpieza'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Precio COP'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Contraseña'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'instagram_link', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Apellido'}),
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Usuario de Acceso'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email (Opcional)'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'WhatsApp'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://instagram.com/...'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.EMPLOYEE
        if commit:
            user.save()
        return user
