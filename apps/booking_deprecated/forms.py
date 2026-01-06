from django import forms
from .models import EmployeeSchedule
from apps.core.models import User
from apps.businesses.models import OperatingHour
import datetime

class EmployeeScheduleForm(forms.ModelForm):
    class Meta:
        model = EmployeeSchedule
        fields = ['start_time', 'end_time', 'break_start', 'break_end', 'is_active_day']
    
    def __init__(self, *args, **kwargs):
        self.business_hour = kwargs.pop('business_hour', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        is_active = cleaned_data.get('is_active_day')

        if is_active and self.business_hour:
            # 1. Validar que el negocio esté abierto ese día
            if self.business_hour.is_closed:
                raise forms.ValidationError("No puedes programar turno un día que el negocio está cerrado.")
            
            # 2. Validar rangos (Lógica Cruzada)
            # Nota: Esto es una validación básica, para turnos nocturnos complejos se requiere lógica extra
            if start and start < self.business_hour.opening_time:
                self.add_error('start_time', f"El negocio abre a las {self.business_hour.opening_time}")
            
            if end and end > self.business_hour.closing_time:
                # Si no es turno nocturno
                if not self.business_hour.crosses_midnight():
                    self.add_error('end_time', f"El negocio cierra a las {self.business_hour.closing_time}")

        return cleaned_data

class EmployeeProfileForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Nueva contraseña (opcional)'}),
        required=False,
        label="Cambiar Contraseña"
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'instagram_link', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
