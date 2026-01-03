#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🚀 Iniciando Deploy de Producción..."

# 1. Instalar librerías
pip install -r requirements.txt

# 2. Recopilar archivos estáticos (CSS, Imágenes)
python manage.py collectstatic --no-input

# 3. Aplicar migraciones (Solo actualiza, NO borra nada)
# Nota: Ya no usamos makemigrations aquí, confiamos en los archivos del repo.
python manage.py migrate

echo "✅ Deploy Finalizado Exitosamente."