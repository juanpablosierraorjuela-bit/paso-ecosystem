import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def fix_settings():
    settings_path = BASE_DIR / 'config' / 'settings.py'
    
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Agregar STATIC_ROOT si no existe
    if 'STATIC_ROOT' not in content:
        content = content.replace(
            "STATIC_URL = 'static/'",
            "STATIC_URL = 'static/'\nSTATIC_ROOT = BASE_DIR / 'staticfiles'\nSTATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'"
        )
        print("✅ STATIC_ROOT configurado.")

    # 2. Agregar Middleware de Whitenoise
    if 'whitenoise.middleware.WhiteNoiseMiddleware' not in content:
        content = content.replace(
            "'django.middleware.security.SecurityMiddleware',",
            "'django.middleware.security.SecurityMiddleware',\n    'whitenoise.middleware.WhiteNoiseMiddleware',"
        )
        print("✅ WhiteNoise Middleware agregado.")
    
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_requirements():
    req_path = BASE_DIR / 'requirements.txt'
    with open(req_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'whitenoise' not in content:
        with open(req_path, 'a', encoding='utf-8') as f:
            f.write('\nwhitenoise>=6.6.0\ngunicorn>=21.2.0')
        print("✅ Whitenoise y Gunicorn agregados a requirements.txt.")

def fix_static_folder():
    static_dir = BASE_DIR / 'static'
    os.makedirs(static_dir, exist_ok=True)
    # Crear un archivo .keep para que Git suba la carpeta
    with open(static_dir / '.keep', 'w') as f:
        f.write('')
    print("✅ Carpeta static creada y asegurada para Git.")

if __name__ == "__main__":
    print("🚑 INICIANDO REPARACIÓN DE STATIC FILES...")
    fix_settings()
    fix_requirements()
    fix_static_folder()
    print("🚀 REPARACIÓN COMPLETADA. Ahora sube los cambios a GitHub.")