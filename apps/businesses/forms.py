from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from apps.core_saas.models import User
from .models import Salon, Service, Employee, EmployeeSchedule

# ... (Se mantiene OwnerSignUpForm igual, no lo toco para no romper registro) ...
class OwnerSignUpForm(UserCreationForm):
    salon_name = forms.CharField(label="Nombre del Negocio", widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(label="Ciudad", widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(label="Dirección", widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(label="WhatsApp", widget=forms.TextInput(attrs={'class': 'form-control'}))
    instagram_link = forms.URLField(label="Instagram", required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    maps_link = forms.URLField(label="Maps", required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.role = 'OWNER'
        user.save()
        Salon.objects.create(
            owner=user, name=self.cleaned_data['salon_name'], city=self.cleaned_data['city'],
            address=self.cleaned_data['address'], whatsapp_number=self.cleaned_data['phone'],
            instagram_link=self.cleaned_data.get('instagram_link'), maps_link=self.cleaned_data.get('maps_link')
        )
        return user

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'description', 'city', 'address', 'whatsapp_number', 'instagram_link', 'maps_link', 
                  'opening_time', 'closing_time', 'work_monday', 'work_tuesday', 'work_wednesday', 
                  'work_thursday', 'work_friday', 'work_saturday', 'work_sunday', 'deposit_percentage']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-control'}),
            'maps_link': forms.URLInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'deposit_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'buffer_time', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'buffer_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class EmployeeForm(forms.ModelForm):
    # Campos virtuales para crear el usuario del empleado
    username = forms.CharField(label="Usuario de Acceso", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Employee
        fields = ['name', 'phone', 'instagram_link', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        employee = super().save(commit=False)
        # Aquí la magia de crear el User se hace en la vista o manualmente
        return employee

class EmployeeScheduleForm(forms.ModelForm):
    class Meta:
        model = EmployeeSchedule
        fields = ['monday_hours', 'tuesday_hours', 'wednesday_hours', 'thursday_hours', 'friday_hours', 'saturday_hours', 'sunday_hours']
        widgets = {
            'monday_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:00-18:00'}),
            'tuesday_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:00-18:00'}),
            'wednesday_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:00-18:00'}),
            'thursday_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:00-18:00'}),
            'friday_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:00-18:00'}),
            'saturday_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '09:00-18:00'}),
            'sunday_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CERRADO'}),
        }
