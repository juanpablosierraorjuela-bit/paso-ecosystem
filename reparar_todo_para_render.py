import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def arreglar_settings():
    settings_path = BASE_DIR / 'config' / 'settings.py'
    print(f"🔧 Reparando: {settings_path}")
    
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # EL CAMBIO CRÍTICO: Reemplazar la configuración de DB fija por la dinámica
    db_vieja = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}"""
    
    db_nueva = """# --- BASE DE DATOS (Híbrida: Render vs Local) ---
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600
    )
}"""
    
    if "dj_database_url.config" not in content:
        # Intentamos reemplazo exacto
        if db_vieja in content:
            content = content.replace(db_vieja, db_nueva)
            print("   ✅ Base de datos configurada para producción.")
        else:
            print("   ⚠️ No encontré el bloque exacto de DATABASES. Revisa manualmente.")
    else:
        print("   ℹ️ La base de datos ya estaba bien configurada.")

    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)

def arreglar_dockerfile():
    docker_path = BASE_DIR / 'Dockerfile'
    print(f"🐳 Reparando: {docker_path}")
    
    # Contenido CORRECTO y COMPLETO del Dockerfile
    nuevo_docker = """FROM python:3.12-slim

# Evita archivos .pyc y asegura logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Instalar dependencias del sistema (necesario para Postgres)
RUN apt-get update && apt-get install -y \\
    libpq-dev \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar el código del proyecto
COPY . /app/

# Recopilar estáticos (CSS/JS) durante la construcción
RUN python manage.py collectstatic --noinput

# --- COMANDO DE INICIO MAESTRO ---
# 1. Ejecuta migraciones (crea tablas en la DB de Render)
# 2. Inicia el servidor web profesional (Gunicorn)
CMD python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
"""
    
    with open(docker_path, 'w', encoding='utf-8') as f:
        f.write(nuevo_docker)
    print("   ✅ Dockerfile actualizado con comando de migración automática.")

if __name__ == "__main__":
    print("=== 🚀 INICIANDO REPARACIÓN PARA RENDER ===")
    try:
        arreglar_settings()
        arreglar_dockerfile()
        print("\n✨ ¡Archivos listos! Ahora sigue las instrucciones finales.")
    except Exception as e:
        print(f"\n❌ Ocurrió un error: {e}")