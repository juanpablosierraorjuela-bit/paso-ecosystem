#!/bin/bash

# Salir si ocurre algún error
set -o errexit
set -o pipefail
set -o nounset

echo "🚀 Iniciando Deployment en Render..."

# 1. Aplicar migraciones a la Base de Datos
echo "📦 Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

# 2. Recolectar archivos estáticos (CSS, JS, Imágenes)
echo "🎨 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# 3. Crear superusuario si no existe (Opcional, requiere variables de entorno)
# python manage.py createsuperuser --noinput || true

# 4. Iniciar Gunicorn (Servidor de Producción)
echo "🔥 Iniciando servidor Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --log-level info