import os
import re
import sys
import subprocess

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
MODELS_PATH = os.path.join(APP_DIR, "models.py")
FORMS_PATH = os.path.join(APP_DIR, "forms.py")
VIEWS_PATH = os.path.join(APP_DIR, "views.py")

# --- CONTENIDO FORMULARIOS (forms.py) ---
# Definimos todo explícitamente para evitar errores de importación
CONTENIDO_FORMS = """from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, Employee

User = get_user_model()

class OwnerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Crea una contraseña segura'
    }), label="Contraseña")
    
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Repite la contraseña'
    }), label="Confirmar Contraseña")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@email.com'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario para iniciar sesión'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'address', 'phone', 'whatsapp', 'instagram']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Estética Divina'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Calle 123 # 45-67, Bogotá'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono fijo o celular'}),
            'whatsapp': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+57 300 123 4567'
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'tu_usuario_instagram'
            }),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
"""

# --- LÓGICA DE LA VISTA (Para views.py) ---
CONTENIDO_VIEW_APPEND = """

# --- INYECCIÓN FINAL ---
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from .forms import OwnerRegistrationForm, SalonForm

class RegisterOwnerView(CreateView):
    template_name = 'registration/register_owner.html'
    form_class = OwnerRegistrationForm 
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = OwnerRegistrationForm()
        if 'salon_form' not in context:
            context['salon_form'] = SalonForm()
        return context

    def post(self, request, *args, **kwargs):
        user_form = OwnerRegistrationForm(request.POST)
        salon_form = SalonForm(request.POST)
        
        if user_form.is_valid() and salon_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            salon = salon_form.save(commit=False)
            salon.owner = user
            salon.save()
            
            from django.contrib.auth import login
            login(request, user)
            return redirect('home')
        
        return render(request, self.template_name, {
            'user_form': user_form,
            'salon_form': salon_form
        })
"""

def forzar_campos_modelos():
    print("🔨 1. Inyectando campos en models.py a la fuerza...")
    
    if not os.path.exists(MODELS_PATH):
        print("❌ Error: No encuentro models.py")
        sys.exit(1)

    with open(MODELS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Campos que necesitamos
    nuevos_campos = """
    # --- CAMPOS INYECTADOS ---
    phone = models.CharField(max_length=50, verbose_name='Teléfono', blank=True, default='')
    whatsapp = models.CharField(max_length=50, blank=True, verbose_name='WhatsApp')
    instagram = models.CharField(max_length=100, blank=True, verbose_name='Instagram')
    # -------------------------
"""

    # Buscamos la definición exacta de la clase Salon
    patron_clase = r"class\s+Salon\s*\(models\.Model\)\s*:"
    
    if re.search(patron_clase, content):
        # Verificamos si ya tiene phone DENTRO de Salon (inspección simple)
        # Para estar seguros, reemplazamos la linea de definición por la linea + campos
        # Esto pone los campos al principio de la clase.
        new_content = re.sub(
            patron_clase, 
            f"class Salon(models.Model):{nuevos_campos}", 
            content, 
            count=1
        )
        
        with open(MODELS_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("   -> ¡Éxito! Campos inyectados directamente en la clase Salon.")
    else:
        print("❌ CRÍTICO: No encontré 'class Salon(models.Model):' en el archivo. Verifica tu código.")
        sys.exit(1)

def escribir_forms_y_views():
    print("📝 2. Reescribiendo forms.py y views.py...")
    
    with open(FORMS_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_FORMS)
    
    # Para views, leemos y agregamos al final, asegurando imports
    with open(VIEWS_PATH, "r", encoding="utf-8") as f:
        views_content = f.read()
    
    # Limpiamos inyecciones previas para no repetir
    if "# --- INYECCIÓN FINAL ---" in views_content:
        views_content = views_content.split("# --- INYECCIÓN FINAL ---")[0]

    with open(VIEWS_PATH, "w", encoding="utf-8") as f:
        f.write(views_content + CONTENIDO_VIEW_APPEND)
    
    print("   -> Archivos actualizados.")

def ejecutar_migraciones():
    print("⚙️ 3. Ejecutando migraciones...")
    # Primero hacemos makemigrations SOLO de businesses para aislar el cambio
    try:
        subprocess.run([sys.executable, "manage.py", "makemigrations", "businesses"], check=True)
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print("✅ ¡Base de datos sincronizada!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en migraciones: {e}")
        print("Intenta correr 'python manage.py makemigrations' manualmente.")

if __name__ == "__main__":
    print("🚀 MODO REPARACIÓN INFALIBLE 🚀")
    forzar_campos_modelos()
    escribir_forms_y_views()
    ejecutar_migraciones()
    print("\n✨ Proceso terminado. Si ves '✅', todo está listo.")