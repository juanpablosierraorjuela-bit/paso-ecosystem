from django import forms
from .models import Salon, Service, Employee

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'description', 'city', 'address', 'whatsapp_number', 'instagram_link', 'maps_link']
        
        # LABELS: Lo que sale encima de la cajita
        labels = {
            'name': 'Nombre del Negocio',
            'description': 'Descripción Corta',
            'city': 'Ciudad',
            'address': 'Dirección del Local',
            'whatsapp_number': 'Número de WhatsApp',
            'instagram_link': 'Link de Instagram',
            'maps_link': 'Link de Google Maps'
        }

        # WIDGETS: Así es como se ven las cajitas (Estilo Bootstrap)
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg', 
                'placeholder': 'Ej: Barbería El Capo'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Ej: Expertos en cortes clásicos y modernos...'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Bogotá, Medellín, Cali...'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Calle 85 # 15-20, Local 1'
            }),
            'whatsapp_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: 300 123 4567 (Solo el número)'
            }),
            'instagram_link': forms.URLInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: https://instagram.com/tu_usuario'
            }),
            'maps_link': forms.URLInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Pega aquí el link de ubicación de Google Maps'
            }),
        }

    def clean_whatsapp_number(self):
        """
        Lógica Inteligente :
        Si el usuario escribe '3001234567', nosotros le ponemos el '57' al principio.
        Si escribe '+57300...', limpiamos el '+' y lo dejamos bien.
        """
        number = self.cleaned_data.get('whatsapp_number')
        if not number:
            return ""
        
        # 1. Eliminar espacios, guiones o símbolos raros
        number = ''.join(filter(str.isdigit, number))

        # 2. Si empieza por '3', asumimos que es Colombia y le falta el 57
        if number.startswith('3') and len(number) == 10:
            number = '57' + number
        
        # 3. Si ya empieza por 57, lo dejamos quieto.
        return number

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'price', 'is_active']
        labels = {
            'name': 'Nombre del Servicio',
            'duration': 'Duración (minutos)',
            'price': 'Precio ($)',
            'is_active': '¿Servicio Activo?'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corte de Cabello'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Detalles del servicio...'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '30'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '25000'}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'phone', 'is_active']
        labels = {
            'name': 'Nombre del Profesional',
            'phone': 'Teléfono de Contacto',
            'is_active': '¿Empleado Activo?'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 300 123 4567'}),
        }
