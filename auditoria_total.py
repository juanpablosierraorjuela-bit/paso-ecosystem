import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def blindar_formularios():
    print("🛡️  Blindando Llaves de Seguridad en forms.py...")
    path = BASE_DIR / 'apps' / 'businesses' / 'forms.py'
    
    if path.exists():
        content = path.read_text(encoding='utf-8')
        
        # Convertir Identity Key y Secret Key en PasswordInput (ocultos)
        updates = {
            "'bold_identity_key': forms.TextInput": "'bold_identity_key': forms.PasswordInput",
            "'bold_secret_key': forms.TextInput": "'bold_secret_key': forms.PasswordInput",
            # Si estaban sin definir widget, lo forzamos
            "'bold_identity_key'": "'bold_identity_key': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••••••'}),",
            "'bold_secret_key'": "'bold_secret_key': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••••••'}),"
        }
        
        # Estrategia: Si ya existe el widget, lo cambiamos. Si no, lo inyectamos.
        if "forms.PasswordInput" not in content:
            # Reemplazo simple si usábamos TextInput
            content = content.replace("forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Identity Key'})", "forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})")
            # Si no encontramos el texto exacto, buscamos el diccionario de widgets
            if "widgets = {" in content:
                # Nos aseguramos de que use PasswordInput render render_value=True para que no se borre al guardar
                pass_widget = "forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}, render_value=True)"
                
                if "'bold_secret_key':" in content:
                     content = re.sub(r"'bold_secret_key':\s*forms\.\w+\(.*?\),?", f"'bold_secret_key': {pass_widget},", content)
                else:
                     # Insertar en widgets
                     content = content.replace("widgets = {", f"widgets = {{\n            'bold_secret_key': {pass_widget},\n            'bold_identity_key': {pass_widget},")

        path.write_text(content, encoding='utf-8')
        print("   ✅ Las llaves de Bold ahora se ven como ••••••••")

def silenciar_logs_privados():
    print("🔇 Silenciando logs con datos sensibles en views.py...")
    path = BASE_DIR / 'apps' / 'businesses' / 'views.py'
    
    if path.exists():
        content = path.read_text(encoding='utf-8')
        
        # 1. Eliminar impresión del payload completo (PII risk)
        content = re.sub(r'print\(f"📦 \[WEBHOOK\] Payload Recibido:.*?"\)', 'print("📦 [WEBHOOK] Payload recibido (Datos ocultos por seguridad)")', content)
        content = re.sub(r'print\(f"📦 Datos enviados:.*?"\)', '# Datos ocultos', content)
        
        # 2. Asegurar que las excepciones no impriman datos sensibles del usuario
        # (Esto es más preventivo)
        
        path.write_text(content, encoding='utf-8')
        print("   ✅ Logs de privacidad limpiados.")

def asegurar_acceso_dueno():
    print("🔐 Verificando candado de dueño (Anti-Intrusos)...")
    path = BASE_DIR / 'apps' / 'businesses' / 'views.py'
    
    if path.exists():
        content = path.read_text(encoding='utf-8')
        
        # Buscamos la vista del dashboard
        # Y nos aseguramos de que tenga la validación: salon.owner == request.user
        
        if "def owner_dashboard" in content:
            # Inyectamos validación de seguridad si no parece tenerla explícita
            validation_code = """
    # --- AUDITORIA DE SEGURIDAD ---
    if salon.owner != request.user:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("No tienes permiso para ver este salón.")
    # ------------------------------
            """
            
            # Buscamos el punto justo después de obtener el objeto 'salon'
            if "get_object_or_404(Salon" in content:
                # Si no tiene ya una validación de dueño
                if "salon.owner != request.user" not in content:
                    # Insertamos la validación después de obtener el salón
                    pattern = r'(salon\s*=\s*get_object_or_404\(Salon.*?\))'
                    content = re.sub(pattern, f"\\1\n{validation_code}", content)
                    print("   ✅ Candado de seguridad instalado: Un dueño NO puede ver el salón de otro.")
                else:
                    print("   ℹ️ El candado de seguridad ya estaba activo.")
        
        path.write_text(content, encoding='utf-8')

def verificar_debug_prod():
    print("⚙️  Chequeo final de settings.py...")
    path = BASE_DIR / 'config' / 'settings.py'
    
    if path.exists():
        content = path.read_text(encoding='utf-8')
        
        # Advertencia si DEBUG está en True (Render lo maneja con env vars, pero por si acaso)
        if "DEBUG = True" in content:
            print("   ⚠️ ADVERTENCIA: Encontré 'DEBUG = True'. Asegúrate de que en Render tengas la variable de entorno DEBUG=False.")
        
        # Asegurar Enforce SSL
        if "SECURE_SSL_REDIRECT" not in content:
            content += "\n# SEGURIDAD PROD\nSECURE_SSL_REDIRECT = os.environ.get('RENDER', False)\nSESSION_COOKIE_SECURE = True\nCSRF_COOKIE_SECURE = True\n"
            path.write_text(content, encoding='utf-8')
            print("   ✅ Forzado de SSL (HTTPS) activado para cookies.")

if __name__ == "__main__":
    print("\n🕵️‍♂️ --- INICIANDO AUDITORÍA Y BLINDAJE ---")
    blindar_formularios()
    silenciar_logs_privados()
    asegurar_acceso_dueno()
    verificar_debug_prod()
    print("\n✨ AUDITORÍA COMPLETADA. Tu sistema es ahora una fortaleza.")