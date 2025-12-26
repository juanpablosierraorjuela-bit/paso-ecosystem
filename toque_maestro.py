import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def aplicar_cambios_finales():
    print("🎩 APLICANDO TOQUES MAESTROS FINALES...")
    
    templates_dir = BASE_DIR / 'templates'
    if not templates_dir.exists():
        print("❌ Error: No encuentro la carpeta templates.")
        return

    # 1. EL FAVICON DE LUJO (P Negra Estilo Vogue)
    favicon_tag = """<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><style>text{font-family:'Didot','Playfair Display','Times New Roman',serif;font-weight:bold;}</style><circle cx=%2250%22 cy=%2250%22 r=%2248%22 fill=%22white%22 stroke=%22black%22 stroke-width=%224%22/><text x=%2250%22 y=%2255%22 font-size=%2260%22 fill=%22black%22 text-anchor=%22middle%22 dominant-baseline=%22middle%22>P</text></svg>">"""

    # 2. RECORRER TODOS LOS HTML
    archivos_modificados = 0
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith(".html"):
                path = Path(root) / file
                try:
                    content = path.read_text(encoding='utf-8')
                    original_content = content
                    cambio_hecho = False

                    # --- A. INSERTAR FAVICON GLOBAL ---
                    # Si tiene <head> y no tiene ya el icono puesto
                    if "<head>" in content and "rel=\"icon\"" not in content:
                        # Lo ponemos justo antes de cerrar el head para que tenga prioridad
                        if "</head>" in content:
                            content = content.replace("</head>", f"    {favicon_tag}\n</head>")
                            print(f"   💎 Favicon instalado en: {file}")
                            cambio_hecho = True
                    
                    # --- B. MENSAJE "AGENDA 24/7" ---
                    # Buscamos donde dice "Cerrado" en las etiquetas visuales (Badges)
                    # Usamos regex para encontrar >Cerrado< o > Cerrado <
                    # Y lo reemplazamos respetando el HTML
                    if "Cerrado" in content:
                        # Reemplazo seguro: Solo cambia el texto visible, no clases ni lógica
                        nuevo_texto_cerrado = "Cerrado • Agenda 24/7"
                        
                        # Patrón: >Cerrado< (con posibles espacios)
                        content = re.sub(r'>\s*Cerrado\s*<', f'>{nuevo_texto_cerrado}<', content)
                        
                        if content != original_content and not cambio_hecho:
                             print(f"   🌙 Mensaje 24/7 agregado en: {file}")
                             cambio_hecho = True

                    # GUARDAR CAMBIOS
                    if content != original_content:
                        path.write_text(content, encoding='utf-8')
                        archivos_modificados += 1

                except Exception as e:
                    print(f"⚠️ No pude leer {file}: {e}")

    print(f"\n✨ ¡LISTO! Se actualizaron {archivos_modificados} archivos.")
    print("   - El Favicon de lujo ahora está en TODAS las páginas.")
    print("   - Los negocios cerrados ahora dicen 'Agenda 24/7'.")

if __name__ == "__main__":
    aplicar_cambios_finales()