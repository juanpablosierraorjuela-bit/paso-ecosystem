import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def mejorar_forms():
    path = BASE_DIR / 'apps' / 'businesses' / 'forms.py'
    print(f"📝 Agregando guías y ayudas visuales en: {path}")
    
    # Reescribimos forms.py con la configuración de lujo para Placeholders y Help Texts
    nuevo_contenido = """from django import forms
from django.contrib.auth import get_user_model
from .models import Salon, Service, EmployeeSchedule

User = get_user_model()

class SalonIntegrationsForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['name', 'address', 'city', 'opening_time', 'closing_time', 'deposit_percentage', 'telegram_bot_token', 'telegram_chat_id', 'bold_identity_key', 'bold_secret_key', "instagram_url", "whatsapp_number"]
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Salón de Belleza Estilo'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cra 15 # 85-30, Bogotá'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bogotá'}),
            'opening_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'deposit_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 50'}),
            
            # --- TELEGRAM ---
            'telegram_bot_token': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: 123456789:ABC-DefGhiJklMnoPqrStu...'
            }),
            'telegram_chat_id': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: 987654321'
            }),

            # --- BOLD (Seguridad Máxima) ---
            'bold_identity_key': forms.PasswordInput(attrs={
                'class': 'form-control', 
                'placeholder': '••••••••••••••••',
                'autocomplete': 'new-password'
            }, render_value=True),
            
            'bold_secret_key': forms.PasswordInput(attrs={
                'class': 'form-control', 
                'placeholder': '••••••••••••••••',
                'autocomplete': 'new-password'
            }, render_value=True),
            
            'instagram_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/tusalon'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '3001234567'}),
        }
        
        help_texts = {
            'deposit_percentage': 'Porcentaje que debe pagar el cliente para confirmar (Ej: 50%).',
            'telegram_bot_token': 'Copia el token que te da @BotFather al crear tu bot.',
            'telegram_chat_id': 'Tu ID numérico personal. Puedes obtenerlo escribiéndole a @userinfobot.',
            'bold_identity_key': 'La "Identity Key" de tu panel de integración de Bold.',
            'bold_secret_key': 'La "Secret Key" de Bold. (No la compartas con nadie).',
            'instagram_url': 'Link directo a tu perfil de Instagram (Opcional).',
            'whatsapp_number': 'Número para contacto directo (Opcional).'
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'duration_minutes', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Corte de Cabello'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '30'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '25000'}),
        }

class EmployeeCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña segura'}))
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario o Celular'}),
        }

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
    path.write_text(nuevo_contenido, encoding='utf-8')
    print("   ✅ Formularios actualizados con Placeholders y Textos de Ayuda.")

def actualizar_template_dashboard():
    path = BASE_DIR / 'templates' / 'owner_dashboard.html'
    print(f"🎨 Activando visualización de textos de ayuda en: {path}")
    
    if not path.exists():
        print("❌ No encontré owner_dashboard.html")
        return

    content = path.read_text(encoding='utf-8')
    
    # ESTRATEGIA:
    # Vamos a buscar cómo se renderizan los campos. Si el usuario usa un bucle for, inyectamos el help_text.
    # Si no, intentaremos asegurar que al menos los campos importantes lo muestren.
    
    # 1. Buscar bucles de renderizado manual o automático
    # A menudo se usa: {% for field in config_form %} ... {{ field }} ...
    
    # Vamos a inyectar un bloque pequeño de código que muestra el help_text si existe
    codigo_help_text = """
                    {% if field.help_text %}
                        <div class="form-text text-muted small mt-1">
                            <i class="fa fa-info-circle"></i> {{ field.help_text }}
                        </div>
                    {% endif %}
    """
    
    # Si encontramos el renderizado del campo {{ field }}, le pegamos esto abajo
    # Usamos una regex que busque {{ field }} o {{ field|... }} dentro de un bucle
    if "{{ field }}" in content and codigo_help_text.strip() not in content:
        # Reemplazo simple: Donde renderice el campo, agrega la ayuda abajo
        content = content.replace("{{ field }}", "{{ field }}" + codigo_help_text)
        print("   ✅ Inyectada lógica de Help Text en bucles generales.")
    
    # 2. Caso Específico: Si hay renderizado manual de Bold/Telegram (ej: {{ config_form.telegram_bot_token }})
    # Buscamos campos clave y si están renderizados manualmente, les agregamos su ayuda
    campos_clave = ['telegram_bot_token', 'telegram_chat_id', 'bold_identity_key', 'bold_secret_key']
    
    for campo in campos_clave:
        tag_campo = f"{{{{ config_form.{campo} }}}}"
        if tag_campo in content:
            # Verificamos si ya tiene help text
            tag_help = f"{{{{ config_form.{campo}.help_text }}}}"
            if tag_help not in content:
                # Agregamos la ayuda manual
                ayuda_manual = f"""
                {tag_campo}
                <div class="form-text text-muted small mt-1"><i class="fa fa-info-circle"></i> {{{{ config_form.{campo}.help_text }}}}</div>
                """
                content = content.replace(tag_campo, ayuda_manual)
                print(f"   ✅ Ayuda manual agregada para: {campo}")

    path.write_text(content, encoding='utf-8')

if __name__ == "__main__":
    mejorar_forms()
    actualizar_template_dashboard()
    print("\n✨ ¡Listo! Ahora los dueños sabrán exactamente qué escribir.")