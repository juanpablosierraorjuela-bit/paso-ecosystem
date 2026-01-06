import os

# ==========================================
# HERRAMIENTA NUCLEAR DE LIMPIEZA
# ==========================================
command_content = """
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
"""

def main():
    # Crear la ruta para el comando personalizado
    path_dir = 'apps/core/management/commands'
    file_path = os.path.join(path_dir, 'force_reset.py')
    
    print(f"☢️  CREANDO HERRAMIENTA NUCLEAR EN {file_path}...")
    
    try:
        os.makedirs(path_dir, exist_ok=True)
        # Asegurar __init__.py
        with open(os.path.join(path_dir, '__init__.py'), 'w') as f:
            f.write('')
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(command_content)
            
        print("✅ Herramienta creada.")
        print("\n👉 AHORA SIGUE ESTOS PASOS EXACTOS EN TU TERMINAL:")
        print("   1. git add .")
        print("   2. git commit -m 'Add force_reset command'")
        print("   3. git push origin main")
        print("\n⏳ LUEGO DE HACER EL PUSH:")
        print("   Ve a tu Dashboard de Render -> Pestaña 'Shell' -> y escribe:")
        print("   python manage.py force_reset")
        print("   python manage.py migrate")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()