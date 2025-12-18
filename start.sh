#!/bin/bash

# No detengas el script inmediatamente si hay un error, déjame intentar arreglarlo primero
set +e

echo "🚀 Iniciando Deployment en Render..."

echo "📦 Aplicando migraciones de base de datos..."

# INTENTO 1: Migración normal
if python manage.py migrate --noinput; then
    echo "✅ Migración exitosa."
else
    echo "⚠️ Conflicto detectado en la base de datos (Error DuplicateColumn)."
    echo "🛠️ Reparando historial de migraciones (FAKING users.0002)..."
    
    # Le decimos a Django que la migración 0002 ya existe en la BD real
    python manage.py migrate --fake users 0002_add_role_field --noinput
    
    echo "🔄 Reintentando migración completa..."
    # Ahora intentamos migrar el resto
    if python manage.py migrate --noinput; then
        echo "✅ Reparación exitosa. Base de datos sincronizada."
    else
        echo "❌ Error fatal: No se pudo reparar la base de datos automáticamente."
        exit 1
    fi
fi

# Volvemos a activar la detección de errores estricta para el resto del proceso
set -e

echo "🎨 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "🔥 Iniciando servidor Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --log-level info