#!/bin/bash

# Detener si hay error
set -e

echo "--- 🚀 INICIANDO DESPLIEGUE SEGURO ---"

echo "--- 1. Detectando Cambios en Base de Datos ---"
python manage.py makemigrations users businesses --noinput
python manage.py makemigrations --noinput

echo "--- 2. Aplicando Cambios (Migrate) ---"
# fake-initial ayuda si la tabla ya existe pero Django cree que no
python manage.py migrate --fake-initial --noinput

echo "--- 3. Preparando Archivos ---"
python manage.py collectstatic --noinput

echo "--- 4. Encendiendo Motor ---"
# Timeout alto para evitar cierres inesperados al inicio
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --timeout 120