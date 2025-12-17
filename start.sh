#!/bin/bash

# Detener el script si hay errores graves
set -e

echo "--- 🏥 DIAGNÓSTICO Y REPARACIÓN DE ARRANQUE ---"

# 1. Forzar migraciones limpias (detecta cambios en invite_token y customer)
echo "--- Generando migraciones pendientes ---"
python manage.py makemigrations users businesses --noinput
python manage.py makemigrations --noinput

# 2. Aplicar migraciones (con fake-initial para evitar conflictos de tablas existentes)
echo "--- Aplicando cambios a la Base de Datos ---"
python manage.py migrate --fake-initial --noinput

# 3. Recolectar estáticos
echo "--- Preparando archivos estáticos ---"
python manage.py collectstatic --noinput

# 4. Iniciar Gunicorn (Servidor Web)
echo "--- 🚀 INICIANDO SERVIDOR ---"
# Aumentamos el timeout para dar tiempo a procesos lentos
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --timeout 120