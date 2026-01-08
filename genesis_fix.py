import os
import shutil
import subprocess
import sys

def genesis():
    print("🌋 INICIANDO PROTOCOLO GÉNESIS (REINICIO TOTAL) 🌋")

    base_dir = os.getcwd()
    
    # ==========================================
    # 1. ARREGLAR SETTINGS.PY (La causa del error)
    # ==========================================
    print("🛠️ 1. Buscando y corrigiendo settings.py...")
    settings_path = os.path.join(base_dir, 'paso_ecosystem', 'settings.py')
    if not os.path.exists(settings_path):
        settings_path = os.path.join(base_dir, 'config', 'settings.py')
    
    if os.path.exists(settings_path):
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Corrección CRÍTICA: Cambiar AUTH_USER_MODEL
        new_content = content.replace("AUTH_USER_MODEL = 'core.User'", "AUTH_USER_MODEL = 'core_saas.User'")
        # Asegurarnos de que la App esté instalada correctamente
        new_content = new_content.replace("'apps.core'", "'apps.core_saas'")
        
        if new_content != content:
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ settings.py corregido: AUTH_USER_MODEL ahora es 'core_saas.User'.")
        else:
            print("ℹ️ settings.py ya parecía estar bien (o no encontré el texto exacto).")
    else:
        print("❌ ERROR: No encontré settings.py.")

    # ==========================================
    # 2. ELIMINAR MIGRACIONES VIEJAS (Limpieza profunda)
    # ==========================================
    print("🗑️ 2. Eliminando migraciones corruptas...")
    apps_dirs = [
        os.path.join(base_dir, 'apps', 'core_saas', 'migrations'),
        os.path.join(base_dir, 'apps', 'businesses', 'migrations')
    ]
    
    for mig_dir in apps_dirs:
        if os.path.exists(mig_dir):
            for filename in os.listdir(mig_dir):
                if filename != '__init__.py' and filename != '__pycache__':
                    file_path = os.path.join(mig_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print(f"⚠️ No pude borrar {filename}: {e}")
            print(f"✅ Limpiado: {mig_dir}")
        else:
            # Si no existe la carpeta migrations, la creamos
            os.makedirs(mig_dir, exist_ok=True)
            with open(os.path.join(mig_dir, '__init__.py'), 'w') as f:
                pass
            print(f"✅ Creado directorio limpio: {mig_dir}")

    # ==========================================
    # 3. ELIMINAR BASE DE DATOS LOCAL (Opcional pero recomendado)
    # ==========================================
    db_path = os.path.join(base_dir, 'db.sqlite3')
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️ Base de datos local (db.sqlite3) eliminada.")

    # ==========================================
    # 4. REGENERAR MIGRACIONES (Crear las nuevas con nombre correcto)
    # ==========================================
    print("✨ 3. Regenerando migraciones (makemigrations)...")
    try:
        # Ejecutamos makemigrations para core_saas y businesses
        subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'core_saas', 'businesses'], check=True)
        print("✅ ¡Migraciones creadas exitosamente!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al crear migraciones: {e}")
        print("Intenta ejecutar manualmente: python manage.py makemigrations core_saas businesses")
        return

    print("\n🚀 LISTO PARA EL DESPEGUE 🚀")
    print("Ejecuta estos comandos INMEDIATAMENTE para subir todo a GitHub:")
    print("---------------------------------------------------")
    print("git add .")
    print("git commit -m \"Genesis: Reset migrations and fix AUTH_USER_MODEL\"")
    print("git push origin main")
    print("---------------------------------------------------")

if __name__ == "__main__":
    genesis()