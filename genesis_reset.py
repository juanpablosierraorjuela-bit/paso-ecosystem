import os
import shutil
import subprocess
import sys

def run_command(command):
    print(f" Ejecutando: {command}")
    subprocess.run(command, shell=True, check=True)

print("  INICIANDO PROTOCOLO GÉNESIS (RESETEO TOTAL) ")

# 1. ELIMINAR BASE DE DATOS LOCAL
if os.path.exists("db.sqlite3"):
    os.remove("db.sqlite3")
    print("  Base de datos antigua eliminada.")

# 2. ELIMINAR MIGRACIONES VIEJAS (Para regenerarlas limpias)
apps = ["apps/businesses", "apps/core_saas"]
for app in apps:
    migrations_path = os.path.join(app, "migrations")
    if os.path.exists(migrations_path):
        for filename in os.listdir(migrations_path):
            if filename != "__init__.py" and filename.endswith(".py"):
                file_path = os.path.join(migrations_path, filename)
                os.remove(file_path)
                print(f" Eliminada migración corrupta: {filename}")
            # También borrar __pycache__ si existe
            if filename == "__pycache__":
                shutil.rmtree(os.path.join(migrations_path, filename))

# 3. REGENERAR MIGRACIONES Y BASE DE DATOS
print("\n  Construyendo nuevo sistema...")
try:
    run_command("python manage.py makemigrations core_saas")
    run_command("python manage.py makemigrations businesses")
    run_command("python manage.py migrate")
    print(" Base de datos nueva creada exitosamente.")
except Exception as e:
    print(f" Error reconstruyendo: {e}")
    sys.exit(1)

# 4. CREAR SUPERUSUARIO AUTOMÁTICO
# Usuario: admin / Clave: admin123
print("\n Creando Superusuario (admin / admin123)...")
from django.contrib.auth import get_user_model
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paso_ecosystem.settings')
django.setup()

User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@paso.com', 'admin123')
    print(" Superusuario 'admin' creado.")
else:
    print("ℹ El usuario admin ya existe.")

# 5. SUBIR A GITHUB (Esto disparará el arreglo en Render)
print("\n Enviando la cura a la nube (GitHub)...")
try:
    run_command("git add .")
    run_command('git commit -m "Genesis Reset: Base de datos y migraciones nuevas"')
    run_command("git push origin main")
    print("\n ¡PROCESO COMPLETADO!")
    print(" Espera 3 minutos a que Render despliegue.")
    print(" NOTA IMPORTANTE PARA RENDER:")
    print("   Si en Render sigue fallando, entra al 'Shell' de Render y ejecuta:")
    print("   python manage.py flush --no-input")
    print("   python manage.py migrate")
except Exception as e:
    print(f" Error subiendo a Git: {e}")

try:
    os.remove(__file__)
except:
    pass