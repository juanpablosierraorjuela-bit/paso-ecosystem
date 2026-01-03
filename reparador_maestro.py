import os
import sys
import subprocess
from django.conf import settings

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "apps", "businesses")
MODELS_PATH = os.path.join(APP_DIR, "models.py")
FORMS_PATH = os.path.join(APP_DIR, "forms.py")
VIEWS_PATH = os.path.join(APP_DIR, "views.py")
REGISTER_TEMPLATE = os.path.join(BASE_DIR, "templates", "registration", "register_owner.html")

# --- CONTENIDO DE FORMULARIOS (forms.py) ---
# Incluimos ServiceForm y EmployeeForm básicos para evitar errores de importación en views.py
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

# Formularios básicos para evitar errores si views.py los importa
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
"""

# --- LÓGICA DE LA VISTA (Para inyectar en views.py) ---
CONTENIDO_VIEW_APPEND = """

# --- INYECCIÓN DEL SCRIPT REPARADOR ---
from .forms import OwnerRegistrationForm

class RegisterOwnerView(CreateView):
    template_name = 'registration/register_owner.html'
    form_class = OwnerRegistrationForm 
    success_url = '/' # Redirige al home después de registrar

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
            # 1. Crear Usuario
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            # 2. Crear Salón vinculado
            salon = salon_form.save(commit=False)
            salon.owner = user
            salon.save()
            
            # 3. Iniciar sesión y redirigir
            from django.contrib.auth import login
            login(request, user)
            return redirect('home')
        
        return render(request, self.template_name, {
            'user_form': user_form,
            'salon_form': salon_form
        })
"""

def arreglar_modelos():
    print("🔧 1. Verificando campos en models.py...")
    with open(MODELS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    campos_faltantes = []
    
    # Verificamos qué campos faltan
    if "phone =" not in content and "phone=" not in content:
        campos_faltantes.append("    phone = models.CharField(max_length=50, verbose_name='Teléfono', blank=True, default='')")
    if "whatsapp =" not in content:
        campos_faltantes.append("    whatsapp = models.CharField(max_length=50, blank=True, verbose_name='WhatsApp')")
    if "instagram =" not in content:
        campos_faltantes.append("    instagram = models.CharField(max_length=100, blank=True, verbose_name='Instagram')")
        
    if campos_faltantes:
        print(f"   -> Detectados {len(campos_faltantes)} campos faltantes. Inyectando...")
        # Inyectar después de la definición de la clase Salon
        if "class Salon(models.Model):" in content:
            injection = "\n" + "\n".join(campos_faltantes) + "\n"
            new_content = content.replace("class Salon(models.Model):", "class Salon(models.Model):" + injection)
            
            with open(MODELS_PATH, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("   -> models.py actualizado con éxito.")
        else:
            print("   ⚠️ No pude encontrar la clase Salon en models.py. Revisa el archivo manualmente.")
    else:
        print("   -> models.py ya tiene todos los campos necesarios.")

def arreglar_forms():
    print("📝 2. Reconstruyendo forms.py...")
    # Sobrescribimos forms.py completamente para asegurar que tenga todas las clases necesarias
    with open(FORMS_PATH, "w", encoding="utf-8") as f:
        f.write(CONTENIDO_FORMS)
    print("   -> forms.py actualizado con SalonForm, ServiceForm, EmployeeForm y OwnerRegistrationForm.")

def arreglar_views():
    print("👀 3. Actualizando lógica de registro en views.py...")
    with open(VIEWS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Asegurar imports necesarios al inicio si no existen
    imports_to_add = []
    if "from django.shortcuts import" not in content:
        imports_to_add.append("from django.shortcuts import render, redirect")
    if "from django.views.generic import" not in content:
        imports_to_add.append("from django.views.generic import CreateView")
        
    if imports_to_add:
        content = "\n".join(imports_to_add) + "\n" + content

    # Apendizamos la vista al final. Esto sobrescribirá cualquier RegisterOwnerView anterior
    # gracias a cómo funciona Python (la última definición gana).
    with open(VIEWS_PATH, "w", encoding="utf-8") as f:
        f.write(content + CONTENIDO_VIEW_APPEND)
    print("   -> views.py actualizado con RegisterOwnerView robusto.")

def ejecutar_migraciones():
    print("⚙️ 4. Sincronizando base de datos...")
    try:
        subprocess.run([sys.executable, "manage.py", "makemigrations"], check=True)
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print("✅ Base de datos al día.")
    except subprocess.CalledProcessError:
        print("❌ Error en migraciones. Pero es probable que los archivos ya estén arreglados.")
        print("   Intenta correr 'python manage.py makemigrations' manualmente.")

if __name__ == "__main__":
    print("🚀 INICIANDO REPARACIÓN MAESTRA (v3.0) 🚀")
    if os.path.exists(MODELS_PATH):
        arreglar_modelos()
        arreglar_forms()
        arreglar_views()
        ejecutar_migraciones()
        print("\n✨ ¡TODO LISTO! Prueba registrarte en: /registro-dueno/ (o la URL que tenías configurada)")
    else:
        print("❌ No encuentro los archivos en apps/businesses/. ¿Estás en la carpeta correcta?")