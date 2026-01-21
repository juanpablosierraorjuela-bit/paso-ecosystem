import os

def run_fix():
    print("--- Iniciando reparación del Panel de Empleados ---")

    # 1. Definir rutas
    base_dir = "apps/businesses"
    tags_dir = os.path.join(base_dir, "templatetags")
    init_file = os.path.join(tags_dir, "__init__.py")
    filter_file = os.path.join(tags_dir, "custom_filters.py")
    template_file = os.path.join(base_dir, "templates/businesses/employee_dashboard.html")

    # 2. Crear carpetas si no existen
    if not os.path.exists(tags_dir):
        os.makedirs(tags_dir)
        print(f"✅ Carpeta creada: {tags_dir}")

    # 3. Crear __init__.py
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            pass
        print(f"✅ Archivo creado: {init_file}")

    # 4. Crear custom_filters.py con la lógica de split_day
    filter_code = """from django import template

register = template.Library()

@register.filter(name='split_day')
def split_day(value):
    \"\"\"Divide una cadena como '0:Lunes' en ['0', 'Lunes']\"\"\"
    if not value:
        return ["", ""]
    if ":" in str(value):
        return value.split(":")
    return [value, value]
"""
    with open(filter_file, "w", encoding="utf-8") as f:
        f.write(filter_code)
    print(f"✅ Filtros creados en: {filter_file}")

    # 5. Modificar el HTML para cargar los filtros
    if os.path.exists(template_file):
        with open(template_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Verificar si ya tiene el load
        if "{% load custom_filters %}" not in "".join(lines):
            new_lines = []
            inserted = False
            for line in lines:
                new_lines.append(line)
                # Insertar justo después de load humanize
                if "{% load humanize %}" in line and not inserted:
                    new_lines.append("{% load custom_filters %}\n")
                    inserted = True
            
            with open(template_file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"✅ HTML actualizado: {template_file}")
        else:
            print("ℹ️ El HTML ya tenía cargados los filtros.")
    else:
        print(f"❌ Error: No se encontró el archivo {template_file}")

    print("--- Reparación completada con éxito ---")

if __name__ == "__main__":
    run_fix()