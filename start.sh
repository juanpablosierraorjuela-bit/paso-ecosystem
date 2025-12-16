#!/bin/bash

# Detener el script si hay algún error
set -e

echo "--- 0. Creando Migraciones (Si hay cambios en Modelos) ---"
# Esto generará los archivos de migración necesarios para los nuevos campos
python manage.py makemigrations --noinput

echo "--- 1. Aplicando Migraciones de Base de Datos ---"
# Esto aplica los cambios a la base de datos real
python manage.py migrate --noinput

echo "--- 2. Recolectando Archivos Estáticos ---"
python manage.py collectstatic --noinput

echo "--- 3. Iniciando Servidor Gunicorn ---"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000