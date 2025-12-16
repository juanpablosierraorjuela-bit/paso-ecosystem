import os
import django
from django.db import connection

# Configurar Django para que el script funcione
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

def force_create_column():
    print("🚑 INICIANDO REPARACIÓN DE EMERGENCIA DE BASE DE DATOS...")
    with connection.cursor() as cursor:
        try:
            # 1. Intentar agregar la columna invite_token si no existe
            print("--- Intentando crear columna 'invite_token' en tabla 'businesses_salon' ---")
            cursor.execute("""
                ALTER TABLE businesses_salon 
                ADD COLUMN IF NOT EXISTS invite_token uuid NULL;
            """)
            print("✅ Columna 'invite_token' verificada/creada exitosamente.")
            
        except Exception as e:
            print(f"⚠️ Alerta: {e}")
            # No detenemos el script, solo avisamos

        try:
            # 2. Intentar agregar la columna customer_id en booking si falta
            print("--- Intentando crear columna 'customer_id' en tabla 'businesses_booking' ---")
            cursor.execute("""
                ALTER TABLE businesses_booking 
                ADD COLUMN IF NOT EXISTS customer_id bigint NULL;
            """)
            print("✅ Columna 'customer_id' verificada/creada exitosamente.")
            
        except Exception as e:
            print(f"⚠️ Alerta: {e}")

    print("🚑 REPARACIÓN FINALIZADA.")

if __name__ == '__main__':
    force_create_column()