import os
import subprocess
import sys

def create_migration_file():
    # Ruta exacta donde debe ir la migración
    migration_path = os.path.join('apps', 'businesses', 'migrations', '0008_fix_service_db.py')
    
    # El contenido que soluciona el error 500 eliminando la columna 'description'
    content = """from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0007_alter_employeeschedule_options_and_more'),
    ]

    operations = [
        # Ejecutamos SQL directo para borrar la columna que causa el conflicto
        migrations.RunSQL(
            "ALTER TABLE businesses_service DROP COLUMN IF EXISTS description;"
        ),
    ]
"""
    
    print(f"✨ Creando archivo de curación en: {migration_path}...")
    try:
        with open(migration_path, 'w') as f:
            f.write(content)
        print("✅ Archivo creado exitosamente.")
    except Exception as e:
        print(f"❌ Error creando el archivo: {e}")
        sys.exit(1)

def git_push_changes():
    print("\n🚀 Iniciando secuencia de despegue a GitHub...")
    
    commands = [
        ['git', 'add', '.'],
        ['git', 'commit', '-m', 'Magic Fix: Reparacion automatica de base de datos en Render'],
    ]
    
    # 1. Añadir y Commitear
    for cmd in commands:
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            print("⚠️  No hubo cambios nuevos para commitear o hubo un error leve. Continuando...")

    # 2. Intentar Push (detectando rama main o master)
    print("☁️  Subiendo a la nube...")
    try:
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("\n✨ ¡Éxito! Subido a la rama 'main'.")
    except subprocess.CalledProcessError:
        print("⚠️  Falló 'main', intentando con 'master'...")
        try:
            subprocess.run(['git', 'push', 'origin', 'master'], check=True)
            print("\n✨ ¡Éxito! Subido a la rama 'master'.")
        except subprocess.CalledProcessError:
            print("\n❌ Error crítico: No se pudo subir a GitHub. Verifica tu conexión o credenciales.")
            sys.exit(1)

if __name__ == "__main__":
    print("🧙‍♂️ --- INICIANDO PROTOCOLO DE REPARACIÓN PASO ECOSYSTEM ---")
    create_migration_file()
    git_push_changes()
    print("\n✅ Tarea completada. Render detectará el cambio y arreglará la base de datos en unos minutos.")
    print("⏳ Espera a que termine el despliegue en Render y prueba tu Dashboard de nuevo.")