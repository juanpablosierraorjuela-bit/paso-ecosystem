#!/bin/bash

# Detener el script si hay algún error grave, pero permitimos fallos menores en migraciones para intentar auto-fix
set -e

echo "--- 0. Creando Migraciones (Con Auto-Merge) ---"
# El flag --merge ayuda a resolver conflictos automáticos si existen
python manage.py makemigrations --merge --noinput || true
python manage.py makemigrations --noinput

echo "--- 1. Aplicando Migraciones de Base de Datos ---"
python manage.py migrate --noinput

echo "--- 2. Recolectando Archivos Estáticos ---"
python manage.py collectstatic --noinput

echo "--- 3. Iniciando Servidor Gunicorn ---"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000