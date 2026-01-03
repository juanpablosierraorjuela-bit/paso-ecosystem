#!/usr/bin/env bash
set -o errexit

echo "🏗️ Construyendo Proyecto..."
pip install -r requirements.txt

echo "🎨 Recopilando Estáticos..."
python manage.py collectstatic --no-input

echo "🔧 Migraciones..."
# Forzamos creación de tablas nuevas
python manage.py makemigrations core_saas
python manage.py makemigrations businesses
python manage.py makemigrations
python manage.py migrate

echo "✅ Listo para despegar."