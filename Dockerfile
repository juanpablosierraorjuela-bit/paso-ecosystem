FROM python:3.12-slim

# Evita archivos .pyc y asegura logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Instalar dependencias del sistema (necesario para Postgres)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
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
