import os
import shutil
import subprocess
import sys

def reparar_marketplace():
    print("🧹 LIMPIANDO RASTROS ANTIGUOS EN MARKETPLACE...")

    base_dir = os.getcwd()
    
    # 1. ELIMINAR MIGRACIONES DE MARKETPLACE (El origen del error)
    # Debemos borrar marketplace/migrations/0001_initial.py para que se regenere
    marketplace_mig_dir = os.path.join(base_dir, 'apps', 'marketplace', 'migrations')
    
    if os.path.exists(marketplace_mig_dir):
        for filename in os.listdir(marketplace_mig_dir):
            if filename != '__init__.py' and filename != '__pycache__':
                file_path = os.path.join(marketplace_mig_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"⚠️ No pude borrar {filename}: {e}")
        print(f"✅ Migraciones de Marketplace eliminadas.")
    else:
        # Si no existe la carpeta, la creamos vacía
        os.makedirs(marketplace_mig_dir, exist_ok=True)
        with open(os.path.join(marketplace_mig_dir, '__init__.py'), 'w') as f:
            pass

    # 2. BORRAR DB LOCAL OTRA VEZ (Para asegurar consistencia total)
    db_path = os.path.join(base_dir, 'db.sqlite3')
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️ Base de datos local limpiada.")

    # 3. REGENERAR TODO DESDE CERO (El Renacimiento)
    print("\n✨ Regenerando migraciones para TODO el sistema...")
    try:
        # Incluimos 'marketplace' en la lista
        subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'core_saas', 'businesses', 'marketplace'], check=True)
        print("✅ ¡MIGRACIONES CREADAS CORRECTAMENTE!")
        
        print("📥 Construyendo nueva base de datos...")
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("✅ SISTEMA OPERATIVO Y SINCRONIZADO.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return

    print("\n🚀 ¡MISIÓN CUMPLIDA! EL ERROR HA SIDO ELIMINADO.")
    print("Sube esto a GitHub para que Render funcione:")
    print("---------------------------------------------------")
    print("git add .")
    print("git commit -m \"Genesis Final: Reset marketplace migrations\"")
    print("git push origin main")
    print("---------------------------------------------------")

if __name__ == "__main__":
    reparar_marketplace()