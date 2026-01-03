import os
import sys
import textwrap
import subprocess

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory: os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(textwrap.dedent(content).strip())
    print(f"✅ Actualizado: {path}")

print("☢️  ACTUALIZANDO PROTOCOLO DE LIMPIEZA DE BASE DE DATOS...")

# ==============================================================================
# 1. COMANDO FORCE_RESET MEJORADO (BORRADO DINÁMICO TOTAL)
# ==============================================================================
# Esta versión no usa una lista fija. Pregunta a la base de datos qué tablas existen
# y las borra TODAS.
create_file('apps/businesses/management/commands/force_reset.py', """
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Borra ABSOLUTAMENTE TODAS las tablas de la base de datos (Nuclear Option)'

    def handle(self, *args, **kwargs):
        self.stdout.write("☢️  INICIANDO BORRADO TOTAL DE LA BASE DE DATOS...")
        
        with connection.cursor() as cursor:
            # 1. Obtener todas las tablas del esquema público
            cursor.execute(\"\"\"
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            \"\"\")
            tables = cursor.fetchall()
            
            if not tables:
                self.stdout.write("   - La base de datos ya está vacía.")
                return

            # 2. Desactivar restricciones temporalmente (si es posible) o usar CASCADE
            self.stdout.write(f"   - Se encontraron {len(tables)} tablas. Eliminando...")

            for table in tables:
                table_name = table[0]
                try:
                    # DROP TABLE ... CASCADE borra la tabla y cualquier relación que dependa de ella
                    cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')
                    self.stdout.write(f"   - 🗑️  Tabla eliminada: {table_name}")
                except Exception as e:
                    self.stdout.write(f"   - ⚠️  Error borrando {table_name}: {e}")

        self.stdout.write("✨ BASE DE DATOS TOTALMENTE VACÍA. LISTA PARA RENACER.")
""")

print("✅ Script de borrado actualizado a versión Nuclear.")

# ==============================================================================
# 2. SUBIDA AUTOMÁTICA
# ==============================================================================
print("🤖 Preparando envío a Render...")

try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix: Nuclear database reset to fix django_content_type error"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("🚀 ¡ENVIADO! Render detectará el cambio, borrará TODO y reconstruirá desde cero.")
except Exception as e:
    print(f"⚠️ Error al subir (hazlo manual si es necesario): {e}")