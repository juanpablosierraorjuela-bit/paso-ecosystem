# Usar imagen oficial de Python ligera
FROM python:3.10-slim-bullseye

# Evitar archivos .pyc y buffer en logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para PostgreSQL y compilación
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
     build-essential \
     libpq-dev \
     gcc \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements/base.txt /app/requirements.txt
# Si tienes un requirements/production.txt, úsalo aquí en su lugar
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN pip install gunicorn psycopg2-binary whitenoise

# Copiar el resto del proyecto
COPY . /app

# Dar permisos de ejecución al script de inicio
RUN chmod +x /app/start.sh

# Render asigna el puerto dinámicamente, pero exponemos el 8000 por defecto
EXPOSE 8000

# Comando de arranque
CMD ["/app/start.sh"]