#!/usr/bin/env bash
set -o errexit

echo "🛡️  Iniciando Deploy Seguro (Fix Admin Models)..."

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Estáticos
python manage.py collectstatic --no-input

# 3. MIGRACIONES INTELIGENTES
# Primero, detectamos cambios solo en la app que tocamos
echo "🔍 Detectando cambios en modelos..."
python manage.py makemigrations businesses

# Luego aplicamos todo
echo "💾 Guardando cambios en base de datos..."
python manage.py migrate

echo "✅ Sistema Estabilizado y Listo."