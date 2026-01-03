#!/usr/bin/env bash
set -o errexit

echo "🏗️ Construyendo Proyecto (Modo Reparación)..."
pip install -r requirements.txt

echo "🎨 Recopilando Estáticos..."
python manage.py collectstatic --no-input

echo "🧨 LIMPIEZA DE BASE DE DATOS (Fix Error 500)..."
# Ejecutamos el comando que acabamos de crear
# python manage.py force_reset (DESACTIVADO PARA PRODUCCION)

echo "🔧 Regenerando Migraciones..."
# Borramos migraciones locales del servidor (si existen)
rm -rf apps/businesses/migrations/0*
rm -rf apps/core_saas/migrations/0*

# Creamos migraciones nuevas basadas en el código actual
python manage.py makemigrations core_saas
python manage.py makemigrations businesses

echo "💾 Aplicando Nueva Estructura..."
python manage.py migrate

echo "✅ Sistema Reparado y Listo."