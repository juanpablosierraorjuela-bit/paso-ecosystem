import os
import shutil

# --- RUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_MIGRATIONS = os.path.join(BASE_DIR, "apps", "core_saas", "migrations")

def limpiar_migraciones():
    print("🧹 Limpiando historial de migraciones de core_saas...")
    
    if os.path.exists(CORE_MIGRATIONS):
        for filename in os.listdir(CORE_MIGRATIONS):
            file_path = os.path.join(CORE_MIGRATIONS, filename)
            # Borrar todo menos el archivo __init__.py
            if filename != "__init__.py" and filename.endswith(".py"):
                os.remove(file_path)
                print(f"   - Eliminado: {filename}")
            elif filename == "__pycache__":
                shutil.rmtree(file_path)
                print(f"   - Eliminada carpeta: {filename}")
    else:
        print("   ⚠️ No encontré la carpeta de migraciones. Creándola...")
        os.makedirs(CORE_MIGRATIONS)
        with open(os.path.join(CORE_MIGRATIONS, "__init__.py"), "w") as f:
            f.write("")

    print("✨ ¡Carpeta limpia! Lista para crear la migración maestra.")

if __name__ == "__main__":
    limpiar_migraciones()