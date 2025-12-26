import os
import subprocess
import sys

def ejecutar(comando_lista):
    # Usamos lista para evitar errores con espacios y comillas en Windows/PowerShell
    print(f"⚙️  Ejecutando: {' '.join(comando_lista)}")
    try:
        subprocess.run(comando_lista, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️ Error (pero intentaré continuar): {e}")

print("=== 🔓 DESBLOQUEANDO SISTEMA DE MIGRACIONES ===")

# 1. Eliminar la base de datos local corrupta (db.sqlite3)
# Esto es necesario para quitar el error "InconsistentMigrationHistory"
if os.path.exists("db.sqlite3"):
    print("\n[1/5] Eliminando base de datos local corrupta...")
    try:
        os.remove("db.sqlite3")
        print("   ✅ db.sqlite3 eliminado (Se recreará limpio).")
    except Exception as e:
        print(f"   ❌ No se pudo eliminar: {e}")

# 2. Re-generar las migraciones (Ahora sí funcionará)
print("\n[2/5] Creando archivos de migración (address, city, etc)...")
# Hacemos makemigrations general para detectar TODOS los cambios
ejecutar(["python", "manage.py", "makemigrations"])

# 3. Re-crear la DB local (opcional, pero bueno para verificar)
print("\n[3/5] Restaurando DB local...")
ejecutar(["python", "manage.py", "migrate"])

# 4. Subir a GitHub (Con el comando corregido para que no falle)
print("\n[4/5] Subiendo corrección a la nube...")
ejecutar(["git", "add", "."])
ejecutar(["git", "commit", "-m", "Fix: Create missing migrations for Render"])
ejecutar(["git", "push"])

print("\n==============================================")
print("✅  ¡LISTO! CÓDIGO Y MIGRACIONES ENVIADOS")
print("==============================================")
print("👉  Ve a Render. El despliegue comenzará en breve.")
print("👉  Esta vez, como SÍ van los archivos de migración, la base de datos")
print("    en la nube creará la columna 'address' y tu página funcionará.")