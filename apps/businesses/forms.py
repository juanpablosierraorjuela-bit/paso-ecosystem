from django import forms
from .models import Service, OperatingHour

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'buffer_minutes', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corte Clásico'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descripción para el buscador semántico...'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'buffer_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tiempo de limpieza'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class OperatingHourForm(forms.ModelForm):
    class Meta:
        model = OperatingHour
        fields = ['day_of_week', 'opening_time', 'closing_time', 'is_closed']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_closed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        opening = cleaned_data.get('opening_time')
        closing = cleaned_data.get('closing_time')
        is_closed = cleaned_data.get('is_closed')

        if not is_closed and opening and closing:
            # Lógica para permitir amanecida:
            # Si cierra a las 02:00 y abre a las 22:00, es válido (cruza medianoche).
            pass 
        return cleaned_data
