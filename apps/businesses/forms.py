from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from apps.core_saas.models import User
from .models import Salon, Service, Employee

class OwnerSignUpForm(UserCreationForm):
    # --- DATOS DEL NEGOCIO ---
    salon_name = forms.CharField(
        label="Nombre del Negocio",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Barbería Supreme'})
    )
    city = forms.CharField(
        label="Ciudad",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bogotá'})
    )
    address = forms.CharField(
        label="Dirección",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cra 15 # 85-20'})
    )
    
    # --- REDES Y CONTACTO ---
    phone = forms.CharField(
        label="WhatsApp del Negocio",
        help_text="Sin espacios. Nosotros agregamos el +57.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 3001234567'})
    )
    instagram_link = forms.URLField(
        label="Link de Instagram (Opcional)",
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/tu_cuenta'})
    )
    maps_link = forms.URLField(
        label="Link de Google Maps (Opcional)",
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://goo.gl/maps/...'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.role = 'OWNER'
        user.save()
        
        # Lógica +57
        raw_phone = self.cleaned_data['phone']
        clean_phone = ''.join(filter(str.isdigit, raw_phone))
        if clean_phone.startswith('3') and len(clean_phone) == 10:
            clean_phone = '57' + clean_phone
            
        Salon.objects.create(
            owner=user,
            name=self.cleaned_data['salon_name'],
            city=self.cleaned_data['city'],
            address=self.cleaned_data['address'],
            whatsapp_number=clean_phone,
            instagram_link=self.cleaned_data.get('instagram_link', ''),
            maps_link=self.cleaned_data.get('maps_link', '')
        )
        return user

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'description', 'city', 'address', 'whatsapp_number', 'instagram_link', 'maps_link']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-control'}),
            'maps_link': forms.URLInput(attrs={'class': 'form-control'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'price', 'is_active']
        labels = {'duration': 'Duración (min)', 'price': 'Precio ($)'}
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
