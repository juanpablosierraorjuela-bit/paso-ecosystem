import os

# ==============================================================================
# EL FORMULARIO MAESTRO (FUSIÓN DE FASE 2 Y FASE 3)
# ==============================================================================
full_forms_content = """
from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, EmployeeSchedule

User = get_user_model()

# --- FASE 2: REGISTRO DE DUEÑO ---
CIUDADES_COLOMBIA = [
    ('Bogotá', 'Bogotá D.C.'), ('Medellín', 'Medellín'), ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'), ('Cartagena', 'Cartagena'), ('Tunja', 'Tunja'),
    ('Bucaramanga', 'Bucaramanga'), ('Pereira', 'Pereira'), ('Manizales', 'Manizales'),
]

class OwnerRegistrationForm(forms.ModelForm):
    email = forms.EmailField(label="Correo Electrónico", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '******'}))
    phone = forms.CharField(label="WhatsApp Personal", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '300...'}))
    salon_name = forms.CharField(label="Nombre del Negocio", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Barbería Vikingos'}))
    city = forms.ChoiceField(label="Ciudad", choices=CIUDADES_COLOMBIA, widget=forms.Select(attrs={'class': 'form-select'}))
    address = forms.CharField(label="Dirección", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cra 15 # 12-34'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu Apellido'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        user.role = 'OWNER'
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
            Salon.objects.create(
                owner=user,
                name=self.cleaned_data['salon_name'],
                city=self.cleaned_data['city'],
                address=self.cleaned_data['address']
            )
        return user

# --- FASE 3: GESTIÓN INTERNA (SERVICIOS Y EMPLEADOS) ---

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'buffer_time', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corte Clásico'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'buffer_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Limpieza (min)'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EmployeeCreationForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Apellido", widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(label="Celular", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        user.role = 'EMPLOYEE'
        if commit:
            user.save()
        return user

class SalonSettingsForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'description', 'address', 'city', 'deposit_percentage', 'opening_time', 'closing_time', 'maps_link', 'instagram_link']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'deposit_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'maps_link': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram_link': forms.URLInput(attrs={'class': 'form-control'}),
        }
"""

def main():
    path = 'apps/businesses/forms.py'
    print(f"🚑 RECONSTRUYENDO {path} CON TODOS LOS FORMULARIOS...")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(full_forms_content)
        print("✅ Archivo forms.py reparado correctamente.")
        
        print("\n👉 EJECUTA AHORA (Sin copiar los números):")
        print("python manage.py makemigrations")
        print("python manage.py migrate")
        print("git add .")
        print("git commit -m 'Fix: Restore missing OwnerRegistrationForm'")
        print("git push origin main")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()