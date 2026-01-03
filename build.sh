#!/usr/bin/env bash
set -o errexit

echo "🚀 Iniciando Deploy de Producción..."
pip install -r requirements.txt
python manage.py collectstatic --no-input

# Aseguramos migraciones de businesses por si fallaron antes
python manage.py makemigrations businesses
python manage.py migrate

echo "✅ Deploy Finalizado."