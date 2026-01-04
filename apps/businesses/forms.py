from django import forms
from .models import Salon, Service, Employee

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        # Solo pedimos los campos que existen en el modelo
        fields = ['name', 'description', 'city', 'address', 'whatsapp_number', 'instagram_link', 'maps_link']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bogotá, Tunja...'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 573001234567'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/tu_negocio'}),
            'maps_link': forms.URLInput(attrs={'class': 'form-control'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'price', 'is_active']
        labels = {
            'duration': 'Duración (minutos)',
            'price': 'Precio ($)',
            'name': 'Nombre del Servicio'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'phone', 'is_active']
        labels = {
            'name': 'Nombre del Profesional',
            'phone': 'Teléfono'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
