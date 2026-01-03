#!/usr/bin/env bash
set -o errexit

echo "🚀 Iniciando Deploy de Producción..."
pip install -r requirements.txt
python manage.py collectstatic --no-input

echo "🔧 Ejecutando Migraciones..."
# Orden estricto para asegurar que se detecten todos los cambios
python manage.py makemigrations core_saas
python manage.py makemigrations businesses
python manage.py makemigrations
python manage.py migrate

echo "✅ Deploy Finalizado."