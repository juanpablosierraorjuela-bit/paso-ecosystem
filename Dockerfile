FROM python:3.12-slim

# Configuración básica de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Instalar dependencias del sistema (necesario para Postgres)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
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
