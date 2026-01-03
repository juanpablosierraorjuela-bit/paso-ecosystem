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