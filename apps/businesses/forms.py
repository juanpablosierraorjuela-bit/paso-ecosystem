from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee, EmployeeSchedule
from datetime import datetime

User = get_user_model()

# Generador de horas para los desplegables (de 5 AM a 10 PM cada 30 min)
TIME_CHOICES = []
for h in range(5, 23):
    for m in (0, 30):
        time_str = f"{h:02d}:{m:02d}"
        display_str = datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
        TIME_CHOICES.append((time_str, display_str))

class EmployeeScheduleForm(forms.ModelForm):
    # Campos "virtuales" para la interfaz gráfica (no se guardan directo en DB)
    def __init__(self, *args, **kwargs):
        self.salon = kwargs.pop('salon', None)
        super().__init__(*args, **kwargs)
        
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        # Inicializar los campos del formulario basados en los datos guardados (string "09:00-18:00")
        if self.instance.pk:
            for day in days:
                db_val = getattr(self.instance, f"{day}_hours", "CERRADO")
                is_active = db_val != "CERRADO"
                self.fields[f"{day}_active"].initial = is_active
                
                if is_active and '-' in db_val:
                    start, end = db_val.split('-')
                    self.fields[f"{day}_start"].initial = start
                    self.fields[f"{day}_end"].initial = end

        # Bloquear días si el dueño (Salon) no trabaja
        if self.salon:
            map_salon = {
                'monday': self.salon.work_monday, 'tuesday': self.salon.work_tuesday,
                'wednesday': self.salon.work_wednesday, 'thursday': self.salon.work_thursday,
                'friday': self.salon.work_friday, 'saturday': self.salon.work_saturday,
                'sunday': self.salon.work_sunday
            }
            for day, works in map_salon.items():
                if not works:
                    self.fields[f"{day}_active"].disabled = True
                    self.fields[f"{day}_active"].help_text = "Cerrado por el negocio."
                    self.fields[f"{day}_active"].initial = False

    # Definimos los campos explícitamente para el loop
    monday_active = forms.BooleanField(required=False, label="Lunes")
    monday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    monday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)

    tuesday_active = forms.BooleanField(required=False, label="Martes")
    tuesday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    tuesday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)

    wednesday_active = forms.BooleanField(required=False, label="Miércoles")
    wednesday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    wednesday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)

    thursday_active = forms.BooleanField(required=False, label="Jueves")
    thursday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    thursday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)

    friday_active = forms.BooleanField(required=False, label="Viernes")
    friday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    friday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)

    saturday_active = forms.BooleanField(required=False, label="Sábado")
    saturday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    saturday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)

    sunday_active = forms.BooleanField(required=False, label="Domingo")
    sunday_start = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    sunday_end = forms.ChoiceField(choices=TIME_CHOICES, required=False)

    class Meta:
        model = EmployeeSchedule
        fields = [] # No usamos los campos directos del modelo, los calculamos

    def save(self, commit=True):
        schedule = super().save(commit=False)
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            is_active = self.cleaned_data.get(f"{day}_active")
            start = self.cleaned_data.get(f"{day}_start")
            end = self.cleaned_data.get(f"{day}_end")
            
            # Lógica inteligente: Si está activo, guarda "HH:MM-HH:MM". Si no, "CERRADO"
            if is_active and start and end:
                setattr(schedule, f"{day}_hours", f"{start}-{end}")
            else:
                setattr(schedule, f"{day}_hours", "CERRADO")
        
        if commit:
            schedule.save()
        return schedule

# --- Otros formularios (se mantienen igual para no romper nada) ---
class SalonRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    salon_name = forms.CharField(max_length=255)
    city = forms.CharField(max_length=100)
    address = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=50) 
    instagram_link = forms.URLField(required=False)
    maps_link = forms.URLField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2: raise forms.ValidationError("Las contraseñas no coinciden")
        return p2

class SalonSettingsForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'city', 'address', 'whatsapp_number', 'instagram_link', 'maps_link', 
                  'opening_time', 'closing_time', 'deposit_percentage',
                  'work_monday', 'work_tuesday', 'work_wednesday', 'work_thursday', 'work_friday', 'work_saturday', 'work_sunday']
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'price', 'buffer_time', 'is_active']

class EmployeeForm(forms.ModelForm):
    username = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    class Meta:
        model = Employee
        fields = ['name', 'phone', 'instagram_link', 'is_active']
