import os
import subprocess
import textwrap

def print_step(msg): print(f"💎 {msg}")

print("✨ INICIANDO PROTOCOLO DE LUJO AUTOMÁTICO...")

# ==============================================================================
# 1. GENERAR EL ICONO "NIVEL DIOS" (SVG VECTORIAL)
# ==============================================================================
# Creamos un archivo SVG matemático. Esto asegura calidad infinita (no se pixela).
# Diseño: Esfera blanca cerámica con una "P" Serif moderna en negro obsidiana.

svg_content = """<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000000" flood-opacity="0.15"/>
    </filter>
  </defs>
  <circle cx="256" cy="256" r="240" fill="#ffffff" filter="url(#shadow)" />
  
  <path d="M170 110 L170 400 L215 400 L215 290 L270 290 C350 290 390 240 390 190 C390 130 340 110 270 110 L170 110 Z 
           M215 150 L270 150 C310 150 335 165 335 200 C335 235 310 250 270 250 L215 250 L215 150 Z" 
        fill="#000000"/>
</svg>
"""

# Asegurar carpeta
os.makedirs('static/images', exist_ok=True)

# Guardar el archivo
icon_path = 'static/images/favicon.svg'
with open(icon_path, 'w', encoding='utf-8') as f:
    f.write(svg_content)

print_step(f"Icono de lujo forjado en: {icon_path}")

# ==============================================================================
# 2. INYECTARLO EN TODAS LAS PÁGINAS (BASE.HTML)
# ==============================================================================
base_path = 'templates/base.html'

# Código HTML a inyectar
favicon_html = """
    <link rel="icon" type="image/svg+xml" href="{% static 'images/favicon.svg' %}">
    <link rel="apple-touch-icon" href="{% static 'images/favicon.svg' %}">
    <meta name="theme-color" content="#ffffff">
    """

with open(base_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Verificamos si ya está para no duplicar
if "favicon.svg" not in content:
    # Buscamos donde ponerlo (justo después del title)
    if "</title>" in content:
        new_content = content.replace("</title>", "</title>" + favicon_html)
        with open(base_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print_step("Código HTML inyectado en el header del sitio.")
    else:
        print("⚠️ No encontré la etiqueta </title> en base.html. Revisa manualmente.")
else:
    print_step("El código ya estaba instalado.")

# ==============================================================================
# 3. SUBIDA AUTOMÁTICA A LA NUBE
# ==============================================================================
print_step("Subiendo cambios a Render...")

try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Design: Install Luxury Favicon SVG"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("\n🏆 ¡LISTO JEFE! En 2 minutos tu marca se verá profesional en todo internet.")
except Exception as e:
    print(f"❌ Error al subir (hazlo manual): {e}")