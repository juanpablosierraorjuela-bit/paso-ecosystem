import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def reparar_forms():
    path = BASE_DIR / 'apps' / 'businesses' / 'forms.py'
    print(f"📝 Reparando Formulario en: {path}")
    
    # Reescribimos el archivo completo para evitar errores de búsqueda/reemplazo
    # Así garantizamos 100% que el campo 'name' esté disponible.
    nuevo_contenido = """from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, EmployeeSchedule

User = get_user_model()

class SalonIntegrationsForm(forms.ModelForm):
    class Meta:
        model = Salon
        # AGREGAMOS 'name' AL PRINCIPIO
        fields = ['name', 'address', 'city', 'opening_time', 'closing_time', 'deposit_percentage', 'telegram_bot_token', 'telegram_chat_id', 'bold_identity_key', 'bold_secret_key', "instagram_url", "whatsapp_number"]
        widgets = {
            # WIDGET PARA EL NOMBRE (Clase form-control para que se vea bonito)
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de tu Negocio'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección completa (Ej: Cra 10 # 20-30)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'opening_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aseguramos que los campos opcionales también tengan estilo
        campos_extra = ['telegram_bot_token', 'telegram_chat_id', 'bold_identity_key', 'bold_secret_key', 'deposit_percentage', 'instagram_url', 'whatsapp_number']
        for campo in campos_extra:
            if campo in self.fields:
                self.fields[campo].widget.attrs.update({'class': 'form-control'})

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'duration_minutes', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del servicio'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutos'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio'}),
        }

class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = EmployeeSchedule
        fields = ['weekday', 'from_hour', 'to_hour']
        widgets = {
            'weekday': forms.Select(attrs={'class': 'form-select'}),
            'from_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'to_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(nuevo_contenido)
    print("   ✅ forms.py reescrito correctamente con el campo 'name'.")

def reparar_html_dashboard():
    path = BASE_DIR / 'templates' / 'owner_dashboard.html'
    print(f"🎨 Limpiando y organizando HTML en: {path}")
    
    if not path.exists():
        print("❌ No encontré owner_dashboard.html")
        return

    content = path.read_text(encoding='utf-8')

    # 1. LIMPIAR EL DESASTRE ANTERIOR
    # Buscamos y borramos el bloque mal puesto si existe
    patron_malo = re.compile(r'<div class="mb-4">\s*<label.*?Nombre del Negocio.*?\s*</div>', re.DOTALL)
    content = patron_malo.sub('', content) # Borrar lo viejo

    # 2. INSERTAR BIEN PUESTO
    # Buscamos la sección de ubicación para insertar ANTES, pero con estructura de GRID
    # Usamos col-12 para que ocupe todo el ancho arriba de la dirección
    bloque_nombre_nuevo = """
            <div class="row mb-3">
                <div class="col-12">
                    <label class="form-label fw-bold" style="color: #4a4a4a;">Nombre del Negocio</label>
                    {{ config_form.name }}
                </div>
            </div>
            """
    
    if "📍 UBICACIÓN DEL NEGOCIO" in content:
        content = content.replace("📍 UBICACIÓN DEL NEGOCIO", f"📍 UBICACIÓN DEL NEGOCIO\n{bloque_nombre_nuevo}")
        print("   ✅ Campo 'Nombre' re-insertado con diseño limpio (Grid Bootstrap).")
    
    path.write_text(content, encoding='utf-8')

def instalar_favicon_lujo():
    print("💎 Instalando Favicon 'P' de Lujo...")
    
    # Favicon en Base64 (SVG optimizado: P negra Serif elegante)
    favicon_tag = """<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><style>text{font-family:'Didot','Playfair Display','Times New Roman',serif;font-weight:bold;}</style><circle cx=%2250%22 cy=%2250%22 r=%2248%22 fill=%22white%22 stroke=%22black%22 stroke-width=%224%22/><text x=%2250%22 y=%2255%22 font-size=%2260%22 fill=%22black%22 text-anchor=%22middle%22 dominant-baseline=%22middle%22>P</text></svg>">"""
    
    # Archivos donde buscar el <head>
    archivos = ['templates/home.html', 'templates/owner_dashboard.html', 'templates/base.html'] # Agrega base.html si existe
    
    for archivo in archivos:
        p = BASE_DIR / archivo
        if p.exists():
            c = p.read_text(encoding='utf-8')
            # Verificar si ya tiene favicon para no repetir
            if "rel=\"icon\"" not in c:
                # Insertar justo antes de cerrar el head </head>
                if "</head>" in c:
                    c = c.replace("</head>", f"    {favicon_tag}\n</head>")
                    p.write_text(c, encoding='utf-8')
                    print(f"   ✅ Favicon instalado en {archivo}")
                # Si no tiene </head> (raro, pero pasa en parciales), intentar al principio
                elif "{% load static %}" in c:
                    c = c.replace("{% load static %}", f"{{% load static %}}\n{favicon_tag}")
                    p.write_text(c, encoding='utf-8')
                    print(f"   ✅ Favicon forzado en {archivo}")

if __name__ == "__main__":
    reparar_forms()
    reparar_html_dashboard()
    instalar_favicon_lujo()
    print("\n✨ ¡Reparación completada! El diseño ahora debe ser perfecto.")