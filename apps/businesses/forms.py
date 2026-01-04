from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee, EmployeeSchedule
from datetime import datetime

User = get_user_model()

COLOMBIA_CITIES = [("Bogotá", "Bogotá"), ("Medellín", "Medellín"), ("Cali", "Cali"), ("Tunja", "Tunja")]
TIME_CHOICES = [(f"{h:02d}:{m:02d}", datetime.strptime(f"{h:02d}:{m:02d}", "%H:%M").strftime("%I:%M %p")) for h in range(5, 23) for m in (0, 30)]

class EmployeeScheduleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        self.day_fields = []
        days = [('monday', 'Lunes'), ('tuesday', 'Martes'), ('wednesday', 'Miércoles'), ('thursday', 'Jueves'), ('friday', 'Viernes'), ('saturday', 'Sábado'), ('sunday', 'Domingo')]
        
        for code, label in days:
            active_name = f"{code}_active"
            start_name = f"{code}_start"
            end_name = f"{code}_end"
            
            # Campos Dinámicos
            self.fields[active_name] = forms.BooleanField(required=False, label=label, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
            self.fields[start_name] = forms.ChoiceField(choices=TIME_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))
            self.fields[end_name] = forms.ChoiceField(choices=TIME_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))
            
            # Cargar datos iniciales
            db_val = getattr(self.instance, f"{code}_hours", "CERRADO")
            if db_val != "CERRADO" and '-' in db_val:
                s, e = db_val.split('-')
                self.fields[active_name].initial = True
                self.fields[start_name].initial = s
                self.fields[end_name].initial = e
            
            # Bloquear si el salón cierra ese día
            salon_open = getattr(self.salon, f"work_{code}", True)
            if not salon_open:
                self.fields[active_name].widget.attrs['disabled'] = True
                self.fields[active_name].initial = False

            self.day_fields.append((code, {
                'label': label,
                'active_field': self[active_name],
                'start_field': self[start_name],
                'end_field': self[end_name],
                'is_salon_open': salon_open
            }))

    class Meta:
        model = EmployeeSchedule
        fields = []

    def save(self, commit=True):
        instance = super().save(commit=False)
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            if self.cleaned_data.get(f"{day}_active"):
                setattr(instance, f"{day}_hours", f"{self.cleaned_data[day+'_start']}-{self.cleaned_data[day+'_end']}")
            else:
                setattr(instance, f"{day}_hours", "CERRADO")
        if commit: instance.save()
        return instance

class SalonRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    salon_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, widget=forms.Select(attrs={'class': 'form-select'}))
    address = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ['username', 'email']
    def clean_password2(self):
        if self.cleaned_data.get('password1') != self.cleaned_data.get('password2'): raise forms.ValidationError("No coinciden")
        return self.cleaned_data.get('password2')

class SalonSettingsForm(forms.ModelForm):
    city = forms.ChoiceField(choices=COLOMBIA_CITIES, widget=forms.Select(attrs={'class': 'form-select'}))
    class Meta:
        model = Salon
        fields = ['name', 'city', 'address', 'whatsapp_number', 'opening_time', 'closing_time', 'deposit_percentage', 'work_monday', 'work_tuesday', 'work_wednesday', 'work_thursday', 'work_friday', 'work_saturday', 'work_sunday']
        widgets = {'opening_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), 'closing_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})}

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'price', 'buffer_time', 'is_active']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'}), 'duration': forms.NumberInput(attrs={'class': 'form-control'}), 'price': forms.NumberInput(attrs={'class': 'form-control'})}

class EmployeeForm(forms.ModelForm):
    username = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    class Meta:
        model = Employee
        fields = ['name', 'phone', 'instagram_link', 'is_active']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}
