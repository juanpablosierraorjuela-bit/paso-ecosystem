
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "BORRADO NUCLEAR: Elimina todas las tablas de la base de datos para reiniciar de cero."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("⚠️  INICIANDO PROTOCOLO DE LIMPIEZA DE BASE DE DATOS..."))
        
        with connection.cursor() as cursor:
            # Comando SQL para Postgres que borra todo el esquema público y lo recrea
            cursor.execute("DROP SCHEMA public CASCADE;")
            cursor.execute("CREATE SCHEMA public;")
            
        self.stdout.write(self.style.SUCCESS("✅ ¡Base de datos limpia! Lista para el Génesis."))
