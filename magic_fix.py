import os
import subprocess
import sys

def fix_migration_dependency():
    # Ruta del archivo que dio problema
    migration_path = os.path.join('apps', 'businesses', 'migrations', '0008_fix_service_db.py')
    
    # El contenido CORREGIDO: Depende de la 0006 (que sí existe) en vez de la 0007 fantasma
    content = """from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0006_employee_telegram_bot_token_and_more'),
    ]

    operations = [
        # Ejecutamos SQL directo para borrar la columna que causa el conflicto
        migrations.RunSQL(
            "ALTER TABLE businesses_service DROP COLUMN IF EXISTS description;"
        ),
    ]
"""
    
    print(f"🔧 Reparando dependencia en: {migration_path}...")
    try:
        with open(migration_path, 'w') as f:
            f.write(content)
        print("✅ Archivo corregido.")
    except Exception as e:
        print(f"❌ Error escribiendo el archivo: {e}")
        sys.exit(1)

def git_push_changes():
    print("\n🚀 Enviando corrección a GitHub...")
    
    commands = [
        ['git', 'add', '.'],
        ['git', 'commit', '-m', 'Fix: Corregir dependencia de migracion 0008 apuntando a 0006'],
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError:
            print("⚠️  Paso omitido (sin cambios nuevos o error leve).")

    print("☁️  Subiendo cambios...")
    try:
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("\n✨ ¡Éxito! Subido a 'main'.")
    except:
        try:
            subprocess.run(['git', 'push', 'origin', 'master'], check=True)
            print("\n✨ ¡Éxito! Subido a 'master'.")
        except:
            print("\n❌ No se pudo subir. Verifica tu conexión.")

if __name__ == "__main__":
    print("🚑 --- MAGIC FIX v2: REPARANDO LA REPARACIÓN ---")
    fix_migration_dependency()
    git_push_changes()
    print("\n✅ Listo. Render intentará desplegar de nuevo.")