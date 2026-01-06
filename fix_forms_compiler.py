import os

# ==========================================
# REPARACIÓN: APPS/BUSINESSES/FORMS.PY
# ==========================================
forms_content = """from django import forms
from django.contrib.auth import get_user_model
from .models import Service, BusinessProfile, OperatingHour

User = get_user_model()

# 1. FORMULARIO DE SERVICIOS
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

# 2. FORMULARIO DE HORARIOS
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

# 3. FORMULARIO DE EMPLEADOS (¡ESTE FALTABA!)
class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña temporal'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario único'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@empleado.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '300...'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.EMPLOYEE
        if commit:
            user.save()
        return user

# 4. FORMULARIO DE CONFIGURACIÓN DE NEGOCIO (¡ESTE TAMBIÉN FALTABA!)
class BusinessSettingsForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = ['business_name', 'description', 'address', 'google_maps_url', 'deposit_percentage', 'is_open_manually']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'google_maps_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://maps.google.com/...'}),
            'deposit_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_open_manually': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
"""

def main():
    path = 'apps/businesses/forms.py'
    print(f"🚑 REPARANDO {path}...")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(forms_content)
        print("✅ Archivo de formularios reconstruido correctamente.")
        print("\n👉 EJECUTA AHORA:")
        print("   git add .")
        print("   git commit -m 'Fix: Missing forms in businesses app'")
        print("   git push origin main")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()