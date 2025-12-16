#!/bin/bash
set -e

echo "--- 0. FORZANDO MIGRACIONES ---"
# Esto creará una nueva migración '0007_auto...' detectando el invite_token
python manage.py makemigrations businesses
python manage.py makemigrations users
python manage.py migrate --noinput

echo "--- 1. Recolectando Estáticos ---"
python manage.py collectstatic --noinput

echo "--- 2. Iniciando Servidor ---"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000