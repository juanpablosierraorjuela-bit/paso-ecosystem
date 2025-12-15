import os
import sys
import shutil
import subprocess

def run_command(command):
    print(f"🔄 Ejecutando: {command}...")
    try:
        # En Windows usamos shell=True para comandos del sistema
        subprocess.check_call(command, shell=True)
        print("✅ Éxito.")
    except subprocess.CalledProcessError:
        print(f"❌ Error al ejecutar: {command}")
        print("⚠️  Asegúrate de haber quitado las tildes/ñ de tu contraseña en el archivo .env")
        sys.exit(1)

def clean_migrations():
    print("🧹 Buscando archivos de migración corruptos o antiguos...")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Recorrer todas las carpetas buscando 'migrations'
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'migrations' in dirnames:
            migrations_dir = os.path.join(dirpath, 'migrations')
            for filename in os.listdir(migrations_dir):
                if filename != '__init__.py' and filename.endswith('.py'):
                    file_path = os.path.join(migrations_dir, filename)
                    try:
                        os.remove(file_path)
                        print(f"   🗑️  Eliminado: {filename}")
                    except Exception as e:
                        print(f"   ⚠️  No se pudo eliminar {filename}: {e}")

def main():
    print("==========================================")
    print(" 🛠️  AUTO-ARREGLO DE BASE DE DATOS PASO  ")
    print("==========================================")
    
    # 1. Limpiar migraciones viejas (Opcional, pero recomendado si hay conflictos graves)
    confirm = input("¿Quieres borrar todas las migraciones antiguas y recrearlas desde cero? (s/n): ")
    if confirm.lower() == 's':
        clean_migrations()
    
    # 2. Crear nuevas migraciones
    run_command("python manage.py makemigrations")
    
    # 3. Aplicar migraciones a la DB
    run_command("python manage.py migrate")
    
    print("\n✨ ¡Listo! Si no viste letras rojas, todo está arreglado.")
    print("   Ahora intenta correr: python manage.py runserver")

if __name__ == "__main__":
    main()