#!/bin/bash

# Detener el script si hay errores graves
set -e

echo "--- 0. FORZANDO SINCRONIZACIÓN DB ---"
# Forzar detección de cambios en invite_token
python manage.py makemigrations businesses users --noinput
# Aplicar cambios
python manage.py migrate --noinput

echo "--- 1. RECOLECTANDO ESTÁTICOS ---"
python manage.py collectstatic --noinput

echo "--- 2. INICIANDO SERVIDOR ---"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000