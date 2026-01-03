from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Borra ABSOLUTAMENTE TODAS las tablas de la base de datos (Nuclear Option)'

    def handle(self, *args, **kwargs):
        self.stdout.write("☢️  INICIANDO BORRADO TOTAL DE LA BASE DE DATOS...")

        with connection.cursor() as cursor:
            # 1. Obtener todas las tablas del esquema público
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
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