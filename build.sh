#!/usr/bin/env bash
# Exit on error
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Recolectar archivos estáticos (CSS/JS)
python manage.py collectstatic --no-input

# Aplicar migraciones a la base de datos de Render
python manage.py migrate
