#!/bin/bash

# Detener el script si hay algún error grave
set -e

echo "--- 0. EJECUTANDO REPARACIÓN MANUAL DE DB ---"
# Ejecutamos el script que acabamos de crear
python fix_db.py

echo "--- 1. Migraciones Normales (Por si acaso) ---"
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "--- 2. Recolectando Archivos Estáticos ---"
python manage.py collectstatic --noinput

echo "--- 3. Iniciando Servidor Gunicorn ---"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000