from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Service, BusinessProfile, OperatingHour

User = get_user_model()

# --- FORMULARIO DE USUARIO (DUEÑO) ---
class OwnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Contraseña'}), label="Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirmar'}), label="Confirmar")
    
    # Campos del Negocio (Integrados en el mismo registro)
    business_name = forms.CharField(label="Nombre del Negocio", widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Belleza Total'}))
    address = forms.CharField(label="Dirección", widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Calle 123 # 45-67'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'city', 'instagram_link']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}), # Debería ser Select, simplificado por ahora
            'instagram_link': forms.URLInput(attrs={'class': 'form-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.username = self.cleaned_data["email"]
        user.role = User.Role.OWNER
        if commit:
            user.save()
            # Crear el perfil de negocio automáticamente
            BusinessProfile.objects.create(
                owner=user,
                business_name=self.cleaned_data['business_name'],
                address=self.cleaned_data['address']
            )
        return user

# --- FORMULARIOS DEL PANEL (SERVICIOS, EMPLEADOS, ETC) ---
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'buffer_minutes', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input'}),
            'buffer_minutes': forms.NumberInput(attrs={'class': 'form-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.EMPLOYEE
        if commit:
            user.save()
        return user

class BusinessSettingsForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = ['business_name', 'description', 'address', 'google_maps_url', 'deposit_percentage', 'is_open_manually']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'address': forms.TextInput(attrs={'class': 'form-input'}),
            'google_maps_url': forms.URLInput(attrs={'class': 'form-input'}),
            'deposit_percentage': forms.NumberInput(attrs={'class': 'form-input'}),
            'is_open_manually': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
