#!/bin/bash
set -e

echo "--- 0. Reparando Migraciones ---"
# Forzamos deteccion de cambios (invite_token nullable)
python manage.py makemigrations businesses users --noinput
python manage.py makemigrations --noinput

echo "--- 1. Aplicando Cambios a la DB ---"
python manage.py migrate --noinput

echo "--- 2. Recolectando Estáticos ---"
python manage.py collectstatic --noinput

echo "--- 3. Iniciando Servidor ---"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000