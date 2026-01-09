import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
settings_path = BASE_DIR / 'config' / 'settings.py'

email_settings = """
# --- CONFIGURACIÓN DE CORREO (SMTP cPanel) ---
# Leemos las credenciales desde las Variables de Entorno de Render
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'mail.pasotunja.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 465))
EMAIL_USE_SSL = True  # Usualmente cPanel usa SSL en el puerto 465
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f"Soporte PASO <{os.environ.get('EMAIL_HOST_USER')}>"
"""

def enable_email():
    print("📧 HABILITANDO SMTP EN SETTINGS.PY...")
    
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'EMAIL_BACKEND' not in content:
        with open(settings_path, 'a', encoding='utf-8') as f:
            f.write("\n" + email_settings)
        print("✅ Configuración SMTP agregada al final de settings.py")
    else:
        print("ℹ️ La configuración de correo ya existía.")

if __name__ == "__main__":
    enable_email()