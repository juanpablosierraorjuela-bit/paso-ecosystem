#!/bin/bash

# Detener el script si hay algún error
set -e

echo "--- 1. Aplicando Migraciones de Base de Datos ---"
# Esto crea las tablas en la base de datos de Render automáticamente
python manage.py migrate --noinput

echo "--- 2. Recolectando Archivos Estáticos (Por seguridad) ---"
python manage.py collectstatic --noinput

echo "--- 3. Iniciando Servidor Gunicorn ---"
# Inicia la aplicación web en el puerto que Render espera
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000