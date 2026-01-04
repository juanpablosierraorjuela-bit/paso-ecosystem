import os
import subprocess
import sys

# --- CONFIGURACIÓN ---
# Detectamos dónde estamos parados
current_dir = os.getcwd()
project_root = None
possible_roots = [current_dir, os.path.join(current_dir, 'paso_final')]

# Buscamos la carpeta correcta
for path in possible_roots:
    if os.path.exists(os.path.join(path, 'templates', 'base.html')):
        project_root = path
        break

if not project_root:
    print("❌ Error: No encuentro la carpeta del proyecto (templates/base.html).")
    print("   Asegúrate de estar en la carpeta correcta en la terminal.")
    sys.exit(1)

# Rutas de los archivos a eliminar/limpiar
favicon_img = os.path.join(project_root, 'static', 'img', 'favicon.png')
base_html = os.path.join(project_root, 'templates', 'base.html')

print(f"🧹 Iniciando protocolo de limpieza en: {project_root}\n")

# --- PASO 1: ELIMINAR LA IMAGEN ---
if os.path.exists(favicon_img):
    try:
        os.remove(favicon_img)
        print("✅ Archivo 'favicon.png' ELIMINADO correctamente.")
    except Exception as e:
        print(f"❌ No se pudo borrar la imagen: {e}")
else:
    print("⚠️  No encontré el archivo de imagen (quizás ya se borró).")

# --- PASO 2: LIMPIAR EL CÓDIGO HTML ---
if os.path.exists(base_html):
    try:
        with open(base_html, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        found = False
        
        # La línea que buscamos eliminar
        target_snippet = "favicon.png" 

        for line in lines:
            # Si la línea tiene referencia al favicon, LA SALTAMOS (no la agregamos)
            if target_snippet in line and '<link' in line:
                found = True
                print("✅ Línea de código del favicon encontrada y ELIMINADA de base.html.")
                continue # Saltamos esta línea
            new_lines.append(line)

        if found:
            with open(base_html, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        else:
            print("ℹ️  No encontré código de favicon en base.html (está limpio).")
            
    except Exception as e:
        print(f"❌ Error editando base.html: {e}")
else:
    print("❌ No encuentro base.html.")

# --- PASO 3: SUBIR CAMBIOS A GITHUB ---
print("\n🚀 Sincronizando limpieza con GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Refactor: Eliminado rastro de favicon (Limpieza)"], check=True)
    print("✅ Commit de limpieza creado.")
    
    print("☁️  Subiendo cambios a la nube...")
    subprocess.run(["git", "push"], check=True)
    print("\n✨ SISTEMA LIMPIO. No queda rastro del favicon.")
    
except subprocess.CalledProcessError as e:
    print(f"⚠️  Git reportó un detalle: {e}")
except FileNotFoundError:
    print("❌ Git no está instalado.")