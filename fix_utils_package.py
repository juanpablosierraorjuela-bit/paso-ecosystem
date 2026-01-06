import os
import shutil
import subprocess

# --- CONTENIDO REPARADO PARA __init__.py (Telegram) ---
# Nota: Cambiamos la importación de modelos a absoluta para evitar errores dentro del paquete.
utils_init_content = """import requests
from apps.core.models import PlatformSettings

def send_telegram_message(message):
    try:
        config = PlatformSettings.objects.first()
        if not config or not config.telegram_bot_token or not config.telegram_chat_id:
            print("⚠️ Telegram no configurado en el Admin.")
            return False

        url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
        data = {
            "chat_id": config.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, data=data, timeout=5)
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error enviando Telegram: {e}")
        return False
"""

# --- CONTENIDO DE colombia_data.py ---
colombia_data_content = """
COLOMBIA_CITIES = [
    ('', 'Selecciona tu Ciudad...'),
    ('Bogotá D.C.', 'Bogotá D.C.'),
    ('Medellín', 'Medellín'),
    ('Cali', 'Cali'),
    ('Barranquilla', 'Barranquilla'),
    ('Cartagena', 'Cartagena'),
    ('Bucaramanga', 'Bucaramanga'),
    ('Manizales', 'Manizales'),
    ('Pereira', 'Pereira'),
    ('Cúcuta', 'Cúcuta'),
    ('Ibagué', 'Ibagué'),
    ('Santa Marta', 'Santa Marta'),
    ('Villavicencio', 'Villavicencio'),
    ('Pasto', 'Pasto'),
    ('Montería', 'Montería'),
    ('Valledupar', 'Valledupar'),
    ('Popayán', 'Popayán'),
    ('Tunja', 'Tunja'),
    ('Neiva', 'Neiva'),
    ('Armenia', 'Armenia'),
    ('Soacha', 'Soacha'),
    ('Bello', 'Bello'),
    ('Itagüí', 'Itagüí'),
    ('Envigado', 'Envigado'),
    # Agrega más ciudades según necesites
]
"""

def fix_structure():
    print("🚑 Reparando estructura de 'apps/core/utils'...")

    utils_path = 'apps/core/utils'
    utils_file = 'apps/core/utils.py'

    # 1. Si existe el ARCHIVO utils.py, lo eliminamos para crear la CARPETA
    if os.path.isfile(utils_file):
        os.remove(utils_file)
        print(f"🗑️ Archivo antiguo {utils_file} eliminado.")

    # 2. Crear la carpeta si no existe
    if not os.path.exists(utils_path):
        os.makedirs(utils_path)
        print(f"📂 Carpeta {utils_path} creada.")

    # 3. Crear el __init__.py (Con la lógica de Telegram)
    init_path = os.path.join(utils_path, '__init__.py')
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(utils_init_content)
    print(f"✅ Lógica de Telegram migrada a {init_path}")

    # 4. Crear colombia_data.py
    cities_path = os.path.join(utils_path, 'colombia_data.py')
    with open(cities_path, 'w', encoding='utf-8') as f:
        f.write(colombia_data_content)
    print(f"✅ Base de datos de ciudades creada en {cities_path}")

    # 5. Git Push
    try:
        print("🐙 Subiendo corrección a GitHub...")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "fix: Convert apps.core.utils to package"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 ¡Corrección enviada! Render desplegará en breve.")
    except Exception as e:
        print(f"⚠️ Error Git: {e}")

if __name__ == "__main__":
    fix_structure()
    # Autodestrucción
    try:
        os.remove(__file__)
    except:
        pass