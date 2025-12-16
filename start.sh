#!/bin/bash

# Detener el script si hay algún error
set -e

echo "--- 0. Creando Migraciones Automáticas ---"
# Detectar cambios en models.py (Booking, Employee, Salon)
python manage.py makemigrations --noinput

echo "--- 1. Aplicando Migraciones a la Base de Datos ---"
# Aplicar los cambios a la BD real en Render
python manage.py migrate --noinput

echo "--- 2. Recolectando Archivos Estáticos (CSS/JS) ---"
python manage.py collectstatic --noinput

echo "--- 3. Iniciando Servidor Web (Gunicorn) ---"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000