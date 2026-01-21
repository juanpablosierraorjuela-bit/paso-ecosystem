import os

def run_fix():
    print("--- Iniciando Reparación Final (Ruta de Templates Raíz) ---")

    # 1. Rutas de la Aplicación (Para los filtros)
    app_dir = "apps/businesses"
    tags_dir = os.path.join(app_dir, "templatetags")
    init_file = os.path.join(tags_dir, "__init__.py")
    filter_file = os.path.join(tags_dir, "custom_filters.py")

    # 2. Asegurar que los filtros existan en la App
    if not os.path.exists(tags_dir):
        os.makedirs(tags_dir)
    if not os.path.exists(init_file):
        with open(init_file, "w") as f: pass
    
    filter_code = """from django import template
register = template.Library()

@register.filter(name='split_day')
def split_day(value):
    if not value: return ["", ""]
    if ":" in str(value): return value.split(":")
    return [value, value]
"""
    with open(filter_file, "w", encoding="utf-8") as f:
        f.write(filter_code)
    print("✅ Filtros creados/verificados en apps/businesses/templatetags/")

    # 3. BUSCAR EL HTML EN LA CARPETA TEMPLATES DE LA RAÍZ
    # Según tu mensaje: C:\\Users\\ecosi\\Desktop\\paso-ecosystem\\templates\\businesses
    templates_root = "templates"
    target_filename = "employee_dashboard.html"
    found_path = None

    for root, dirs, files in os.walk(templates_root):
        if target_filename in files:
            found_path = os.path.join(root, target_filename)
            break

    if found_path:
        print(f"🔍 Archivo encontrado en: {found_path}")
        with open(found_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Insertar la carga de filtros si no existe
        if "{% load custom_filters %}" not in content:
            # Buscamos humanize para insertar después, o lo ponemos arriba
            if "{% load humanize %}" in content:
                new_content = content.replace(
                    "{% load humanize %}", 
                    "{% load humanize %}\n{% load custom_filters %}"
                )
            else:
                # Si no encuentra humanize, lo pone después del extends
                new_content = content.replace(
                    "{% extends 'base.html' %}", 
                    "{% extends 'base.html' %}\n{% load custom_filters %}"
                )
            
            with open(found_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ HTML actualizado exitosamente.")
        else:
            print("ℹ️ El HTML ya tenía la línea {% load custom_filters %}.")
    else:
        print(f"❌ Error: No se pudo encontrar {target_filename} en la carpeta {templates_root}")

    print("--- Proceso terminado ---")

if __name__ == "__main__":
    run_fix()