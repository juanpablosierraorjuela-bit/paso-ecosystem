import os

# --- NUEVO DOCKERFILE MEJORADO ---
# El cambio clave está en la última línea (CMD):
# Agregamos "python manage.py migrate &&" antes de gunicorn.

NUEVO_DOCKERFILE = """FROM python:3.12-slim

# Evita que Python cree archivos caché (.pyc) y asegura logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define un puerto por defecto (Render lo sobreescribe a 10000, pero esto es un fallback)
ENV PORT=8000

WORKDIR /app

# Instalar dependencias del sistema necesarias (PostgreSQL, compiladores)
RUN apt-get update && apt-get install -y \\
    libpq-dev \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/

# RECOLECCIÓN DE ESTÁTICOS: Asegura que el diseño se vea bien
RUN python manage.py collectstatic --noinput

# --- COMANDO DE INICIO (LA CLAVE DEL ÉXITO) ---
# 1. Ejecuta las migraciones (crea tablas en la DB)
# 2. Inicia el servidor Gunicorn
CMD python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
"""

def arreglar_dockerfile():
    ruta = "Dockerfile"
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(NUEVO_DOCKERFILE)
    print("✅ Dockerfile actualizado: Ahora ejecutará migraciones automáticamente.")

if __name__ == "__main__":
    arreglar_dockerfile()