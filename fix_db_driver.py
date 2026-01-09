import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def fix_driver():
    print("🚑 INSTALANDO RUEDAS DE BASE DE DATOS (psycopg2-binary)...")
    req_path = BASE_DIR / 'requirements.txt'
    
    with open(req_path, 'r') as f:
        content = f.read()
    
    # Agregamos el driver de PostgreSQL
    if 'psycopg2-binary' not in content:
        with open(req_path, 'a') as f:
            f.write('\npsycopg2-binary>=2.9.9')
        print("✅ ¡Listo! Se agregó 'psycopg2-binary' a requirements.txt.")
    else:
        print("ℹ️ El driver ya estaba instalado.")

if __name__ == "__main__":
    fix_driver()