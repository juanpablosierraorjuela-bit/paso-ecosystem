from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, EmployeeSchedule

User = get_user_model()

class SalonIntegrationsForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['address', 'city', 'opening_time', 'closing_time', 'deposit_percentage', 'telegram_bot_token', 'telegram_chat_id', 'bold_identity_key', 'bold_secret_key', "instagram_url", "whatsapp_number"]
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección completa (Ej: Cra 10 # 20-30)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'opening_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['telegram_bot_token'].widget.attrs.update({'class': 'form-control', 'placeholder': '123456:ABC-DEF...'})
        self.fields['telegram_chat_id'].widget.attrs.update({'class': 'form-control', 'placeholder': 'ID numérico'})
        self.fields['bold_identity_key'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Identity Key'})
        self.fields['bold_secret_key'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Secret Key'})
        self.fields['deposit_percentage'].widget.attrs.update({'class': 'form-control', 'min': '0', 'max': '100', 'placeholder': '% de Abono (ej: 50)'})

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'duration_minutes', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del servicio'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutos'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio'}),
        }

class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = EmployeeSchedule
        fields = ['weekday', 'from_hour', 'to_hour']
        widgets = {
            'weekday': forms.Select(attrs={'class': 'form-select'}),
            'from_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'to_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
