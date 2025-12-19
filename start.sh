#!/bin/bash

# Detener el script si hay algún error
set -e

echo "--- 0. Reparando Migraciones ---"
# Forzamos la creación de migraciones para las apps específicas
python manage.py makemigrations users businesses --noinput
python manage.py makemigrations --noinput

echo "--- 1. Aplicando Migraciones (Falso positivo permitido) ---"
# Intentamos aplicar todo. Si hay error de 'ya existe', continuamos.
python manage.py migrate --noinput || echo "Advertencia: Migración parcial, continuando..."

echo "--- 2. Recolectando Archivos Estáticos ---"
python manage.py collectstatic --noinput

echo "--- 3. Iniciando Servidor Gunicorn ---"
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000