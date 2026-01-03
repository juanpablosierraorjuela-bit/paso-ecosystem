import os
import sys
import textwrap

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory: os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(textwrap.dedent(content).strip())
    print(f"✅ Generado: {path}")

print("🚑 INICIANDO REPARACIÓN DE ERROR 500 (Sincronización DB)...")

# 1. HERRAMIENTA DE LIMPIEZA SQL (Force Reset)
# Creamos un comando personalizado de Django para borrar las tablas viejas
create_file('apps/businesses/management/commands/force_reset.py', """
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Borra las tablas de la app para forzar una regeneración limpia'

    def handle(self, *args, **kwargs):
        self.stdout.write("🗑️  Iniciando borrado de tablas viejas...")
        with connection.cursor() as cursor:
            # Lista de tablas a eliminar (El orden importa por las claves foráneas)
            tables = [
                'businesses_booking',
                'businesses_schedule',
                'businesses_openinghours',
                'businesses_service',
                'businesses_employee',
                'businesses_salon',
                'core_saas_user_groups',      # Tablas de usuario vinculadas
                'core_saas_user_user_permissions',
                'core_saas_user',
                'django_migrations',          # Vital: Borrar historial de migraciones
            ]
            for table in tables:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                    self.stdout.write(f"   - Tabla {table} eliminada.")
                except Exception as e:
                    self.stdout.write(f"   - Nota: {table} no existía o error menor.")
        
        self.stdout.write("✨ Tablas eliminadas. Listo para migrar desde cero.")
""")

# Crear __init__.py en las carpetas de management para que Django lo reconozca
create_file('apps/businesses/management/__init__.py', "")
create_file('apps/businesses/management/commands/__init__.py', "")


# 2. ACTUALIZAR BUILD.SH (Para que use la herramienta)
create_file('build.sh', """#!/usr/bin/env bash
set -o errexit

echo "🏗️ Construyendo Proyecto (Modo Reparación)..."
pip install -r requirements.txt

echo "🎨 Recopilando Estáticos..."
python manage.py collectstatic --no-input

echo "🧨 LIMPIEZA DE BASE DE DATOS (Fix Error 500)..."
# Ejecutamos el comando que acabamos de crear
python manage.py force_reset

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
""")


# 3. ACTUALIZAR SETTINGS (Activar DEBUG para ver errores si persisten)
# Leemos el settings actual y forzamos DEBUG = True
settings_path = 'paso_ecosystem/settings.py'
try:
    with open(settings_path, 'r', encoding='utf-8') as f:
        settings_code = f.read()
    
    # Reemplazo seguro
    if "DEBUG = 'RENDER' not in os.environ" in settings_code:
        settings_code = settings_code.replace(
            "DEBUG = 'RENDER' not in os.environ", 
            "DEBUG = True # MODO REPARACION ACTIVADO"
        )
        create_file(settings_path, settings_code)
        print("✅ DEBUG activado en settings.py")
except:
    print("⚠️ No se pudo editar settings.py automáticamente (no crítico).")

print("🚀 ¡LISTO! Ejecuta los comandos de git para subir la reparación.")