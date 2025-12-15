# 1. Usar una imagen oficial de Python ligera
FROM python:3.10-slim

# 2. Evitar que Python genere archivos .pyc y permitir logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalar dependencias del sistema necesarias para PostgreSQL y otros
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiar los requerimientos e instalarlos
COPY ./requirements /app/requirements
RUN pip install --upgrade pip

# Instalamos base.txt y aseguramos las librerías de producción (gunicorn, whitenoise)
# por si acaso no las pusiste en el archivo de texto.
RUN pip install -r requirements/base.txt && \
    pip install gunicorn whitenoise dj-database-url

# 6. Copiar el resto del código del proyecto
COPY . /app

# 7. Recolectar archivos estáticos (CSS, JS) para que se vean bien en la nube
# Este paso es CRÍTICO para Render
RUN python manage.py collectstatic --noinput

# 8. Exponer el puerto
EXPOSE 8000

# 9. Comando PRO para producción (Gunicorn) en lugar de runserver
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]