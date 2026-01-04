import os
import subprocess
import sys

# --- CONFIGURACIÓN ---
project_root = os.getcwd()
static_img_dir = os.path.join(project_root, 'static', 'img')
base_html_path = os.path.join(project_root, 'templates', 'base.html')
favicon_target = os.path.join(static_img_dir, 'favicon.png')

print(f"🕵️  Analizando carpeta: {static_img_dir}")

# 1. Asegurar que la carpeta exista
os.makedirs(static_img_dir, exist_ok=True)

# 2. BÚSQUEDA INTELIGENTE Y AUTOCORRECCIÓN
if not os.path.exists(favicon_target):
    print("⚠️  No encontré 'favicon.png' exacto. Buscando variantes...")
    
    # Listar qué hay realmente en la carpeta
    try:
        files = os.listdir(static_img_dir)
    except FileNotFoundError:
        files = []

    if not files:
        print("\n❌ LA CARPETA ESTÁ VACÍA.")
        print(f"Ruta revisada: {static_img_dir}")
        print("Por favor, arrastra la imagen a esa carpeta dentro de VS Code.")
        sys.exit(1)
    
    print(f"📁 Archivos que sí encontré: {files}")

    renamed = False
    for filename in files:
        # Si encontramos algo que parece una imagen, lo usamos
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) or 'fav' in filename.lower():
            old_path = os.path.join(static_img_dir, filename)
            print(f"🔧 ¡Ajá! Encontré '{filename}'. Lo voy a renombrar a 'favicon.png' automáticamente.")
            try:
                os.rename(old_path, favicon_target)
                renamed = True
                break
            except OSError as e:
                print(f"❌ Error al renombrar: {e}")

    if not renamed:
        print("❌ Hay archivos, pero ninguno parece una imagen válida para usar.")
        sys.exit(1)
else:
    print("✅ ¡Imagen 'favicon.png' detectada y lista!")

# --- PASO 3: MODIFICAR BASE.HTML ---
print("📝 Configurando base.html...")
try:
    with open(base_html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    favicon_tag = "    <link rel=\"icon\" type=\"image/png\" href=\"{% static 'img/favicon.png' %}\">\n"

    if 'rel="icon"' in content:
        print("ℹ️  El favicon ya estaba configurado en el HTML.")
    else:
        if '</title>' in content:
            new_content = content.replace('</title>', '</title>\n' + favicon_tag)
            with open(base_html_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ HTML actualizado correctamente.")
        else:
            print("⚠️ No encontré la etiqueta </title> para insertar el código.")
except FileNotFoundError:
    print(f"❌ No encuentro el archivo base.html en: {base_html_path}")
    print("Verifica que estás ejecutando el script en la raíz del proyecto.")
    sys.exit(1)

# --- PASO 4: SUBIR A GITHUB ---
print("\n🚀 Subiendo cambios a GitHub...")
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Fix: Favicon agregado (Automático)"], check=True)
    print("✅ Commit creado.")
    
    print("☁️  Enviando a la nube (esto puede tardar unos segundos)...")
    subprocess.run(["git", "push"], check=True)
    print("\n✨ ¡MISIÓN CUMPLIDA! Tu favicon ya debería estar en producción.")
except subprocess.CalledProcessError as e:
    print(f"⚠️  Hubo un detalle con Git (quizás ya estaba actualizado): {e}")
except FileNotFoundError:
    print("❌ No tienes Git instalado o configurado en la terminal.")