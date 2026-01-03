import os
import textwrap
import subprocess

def update_file(path, old_text, new_text):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_text in content:
            content = content.replace(old_text, new_text)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Asegurado: {path}")
        else:
            print(f"ℹ️ {path} ya estaba actualizado o no se encontró el texto.")
    except FileNotFoundError:
        print(f"❌ No se encontró: {path}")

print("🔒 ASEGURANDO SISTEMA PARA PRODUCCIÓN REAL...")

# 1. Quitar la orden de borrado de base de datos
build_path = 'build.sh'
old_build = "python manage.py force_reset"
new_build = "# python manage.py force_reset (DESACTIVADO PARA PRODUCCION)"
update_file(build_path, old_build, new_build)

# 2. Desactivar DEBUG (Volver a modo seguro)
settings_path = 'paso_ecosystem/settings.py'
old_debug = "DEBUG = True # MODO REPARACION ACTIVADO"
new_debug = "DEBUG = 'RENDER' not in os.environ"
update_file(settings_path, old_debug, new_debug)

print("🚀 Enviando candado de seguridad a GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Security: Disable DB reset and DEBUG mode for production"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("🏆 ¡SISTEMA FINALIZADO! Ya puedes registrar negocios reales.")
except Exception as e:
    print(f"Error git: {e}")