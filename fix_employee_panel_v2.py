import os

def run_fix():
    print("--- Iniciando Reparación Inteligente v2.0 ---")

    # 1. Rutas de carpetas
    base_dir = "apps/businesses"
    tags_dir = os.path.join(base_dir, "templatetags")
    init_file = os.path.join(tags_dir, "__init__.py")
    filter_file = os.path.join(tags_dir, "custom_filters.py")

    # 2. Asegurar que los filtros existan (esto ya lo hizo el anterior, pero lo confirmamos)
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
    print("✅ Filtros verificados/creados.")

    # 3. BUSCADOR INTELIGENTE DEL HTML
    # Buscamos en toda la carpeta apps/businesses por el archivo employee_dashboard.html
    target_filename = "employee_dashboard.html"
    found_path = None

    for root, dirs, files in os.walk(base_dir):
        if target_filename in files:
            found_path = os.path.join(root, target_filename)
            break

    if found_path:
        print(f"🔍 Archivo encontrado en: {found_path}")
        with open(found_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Insertar la carga de filtros si no existe
        if "{% load custom_filters %}" not in content:
            # Lo insertamos justo después de {% load humanize %}
            new_content = content.replace(
                "{% load humanize %}", 
                "{% load humanize %}\n{% load custom_filters %}"
            )
            with open(found_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ HTML actualizado exitosamente.")
        else:
            print("ℹ️ El HTML ya tenía la línea necesaria.")
    else:
        print(f"❌ Error: No se pudo encontrar {target_filename} en {base_dir}")

    print("--- Proceso terminado ---")

if __name__ == "__main__":
    run_fix()