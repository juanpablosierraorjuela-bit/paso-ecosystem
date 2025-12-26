import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# 1. CONTENIDO CORRECTO PARA SETTINGS.PY
# Usamos dj_database_url para leer la base de datos de Render automáticamente.
SETTINGS_FIX = """
# --- BASE DE DATOS (Híbrida: Render vs Local) ---
# En Render: Usa DATABASE_URL (PostgreSQL)
# En Local: Usa db.sqlite3 (SQLite)
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600
    )
}
"""

def arreglar_settings():
    settings_path = BASE_DIR / 'config' / 'settings.py'
    print(f"🔧 Reparando configuración en: {settings_path}")
    
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Buscamos la configuración vieja de DATABASES y la reemplazamos
    import re
    # Esta expresión regular busca el bloque DATABASES = { ... }
    pattern = r"DATABASES\s*=\s*\{[^}]+\{[^}]+\}[^}]+\}"
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, SETTINGS_FIX.strip(), content, flags=re.DOTALL)
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ settings.py: Base de datos configurada para Render (dj_database_url).")
    else:
        print("⚠️ No encontré el bloque DATABASES estándar. Verifica manualmente.")

# 2. CONTENIDO CORRECTO PARA DOCKERFILE
# Incluye 'migrate' para crear las tablas al iniciar.
DOCKERFILE_FIX = """FROM python:3.12-slim

# Configuración básica de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Instalar dependencias del sistema (necesario para Postgres)
RUN apt-get update && apt-get install -y \\
    libpq-dev \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Instalar librerías de Python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar el código
COPY . /app/

# Recolectar archivos estáticos (CSS/JS)
RUN python manage.py collectstatic --noinput

# --- COMANDO DE INICIO ---
# 1. Ejecuta migraciones (crea tablas en la DB real)
# 2. Inicia el servidor (Gunicorn)
CMD python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
"""

def arreglar_dockerfile():
    docker_path = BASE_DIR / 'Dockerfile'
    with open(docker_path, 'w', encoding='utf-8') as f:
        f.write(DOCKERFILE_FIX)
    print("✅ Dockerfile: Actualizado con comando de migración automática.")

if __name__ == "__main__":
    try:
        arreglar_settings()
        arreglar_dockerfile()
        print("\n✨ ¡Archivos arreglados! Sigue las instrucciones para desplegar.")
    except Exception as e:
        print(f"❌ Error: {e}")