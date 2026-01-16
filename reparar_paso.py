import os
import re
import subprocess
from datetime import time

def fix_file(path, replacements, imports_to_add=None):
    if not os.path.exists(path):
        print(f"⚠️ No se encontró el archivo: {path}")
        return False
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Añadir imports necesarios
    if imports_to_add:
        for imp in imports_to_add:
            if imp not in content:
                content = imp + "\n" + content

    # Hacer los reemplazos
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)

    if content != new_content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Archivo actualizado: {path}")
        return True
    else:
        print(f"ℹ️ El archivo {path} ya estaba corregido.")
        return False

def run_commands():
    print("\n🚀 Ejecutando comandos de base de datos...")
    try:
        subprocess.run(['python', 'manage.py', 'makemigrations'], check=True)
        subprocess.run(['python', 'manage.py', 'migrate'], check=True)
        print("✨ Migraciones completadas con éxito.")
    except Exception as e:
        print(f"❌ Error al migrar: {e}")

if __name__ == "__main__":
    # 1. Corregir Modelos
    model_replacements = {
        "default='09:00'": "default=time(9, 0)",
        "default='18:00'": "default=time(18, 0)",
        "default='13:00'": "default=time(13, 0)",
        "default='14:00'": "default=time(14, 0)",
        "work_start = models.TimeField": "work_start = models.TimeField(null=True, blank=True, ",
        "work_end = models.TimeField": "work_end = models.TimeField(null=True, blank=True, ",
        "lunch_start = models.TimeField": "lunch_start = models.TimeField(null=True, blank=True, ",
        "lunch_end = models.TimeField": "lunch_end = models.TimeField(null=True, blank=True, ",
    }
    fix_file('apps/businesses/models.py', model_replacements, ["from datetime import time"])

    # 2. Corregir Vistas
    # Aseguramos que el dashboard sea más robusto
    view_replacements = {
        "schedule, created = EmployeeSchedule.objects.get_or_create(employee=request.user)": 
        "schedule, created = EmployeeSchedule.objects.get_or_create(employee=request.user, defaults={'work_start': time(9,0), 'work_end': time(18,0)})"
    }
    fix_file('apps/businesses/views.py', view_replacements, ["from datetime import time"])

    # 3. Ejecutar cambios
    run_commands()
    print("\n🎉 ¡PROCESO FINALIZADO!")
    print("Ahora sube los cambios a GitHub para que Render se actualice.")