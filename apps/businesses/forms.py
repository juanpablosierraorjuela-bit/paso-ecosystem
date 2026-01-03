from django import forms
from .models import Salon, Service, Employee

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'description', 'address', 'city', 'whatsapp_number', 'instagram_link', 'maps_link', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        # AQUÍ ESTABA EL ERROR: Usamos 'duration' que es el nombre correcto en el modelo
        fields = ['name', 'description', 'duration', 'price', 'is_active']
        labels = {
            'duration': 'Duración (minutos)',
            'price': 'Precio ($)',
            'name': 'Nombre del Servicio'
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'phone', 'is_active']
        labels = {
            'name': 'Nombre del Profesional',
            'phone': 'Teléfono'
        }
