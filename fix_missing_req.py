import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def fix_requirements():
    print("🚑 AGREGANDO LIBRERÍA FALTANTE (dj-database-url)...")
    req_path = BASE_DIR / 'requirements.txt'
    
    with open(req_path, 'r') as f:
        content = f.read()
    
    # Verificamos si ya está para no duplicar
    if 'dj-database-url' not in content:
        with open(req_path, 'a') as f:
            f.write('\ndj-database-url>=2.1.0')
        print("✅ ¡Listo! Se agregó 'dj-database-url' a requirements.txt.")
    else:
        print("ℹ️ La librería ya estaba en el archivo.")

if __name__ == "__main__":
    fix_requirements()