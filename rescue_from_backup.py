import os
import shutil
import sys

# ==========================================
# CONFIGURACIÓN DE RESCATE
# ==========================================
# Nombre exacto de tu carpeta de backup (asegúrate que esté al lado de manage.py)
BACKUP_DIR = 'pasofinalbacukp' 

# Lista de tesoros a recuperar (Origen en Backup -> Destino en Proyecto)
FILE_MAPPING = [
    # 1. El Cerebro (Backend)
    ('apps/businesses/views.py', 'apps/businesses/views.py'),
    ('apps/businesses/urls.py', 'apps/businesses/urls.py'),
    ('apps/businesses/forms.py', 'apps/businesses/forms.py'),
    ('apps/businesses/logic.py', 'apps/businesses/logic.py'), # ¡Este es nuevo e importante!
    ('apps/businesses/models.py', 'apps/businesses/models.py'),

    # 2. La Cara (Frontend / Templates)
    # Nota: En el backup se llaman 'dashboard/owner_...', los pasaremos a 'templates/businesses/' 
    # y los renombraremos para que coincidan con la estructura moderna si es necesario, 
    # o mantendremos la estructura del backup si las views apuntan ahí.
    # ESTRATEGIA: Restaurar en 'templates/dashboard' porque las views del backup seguro apuntan allí.
    ('templates/dashboard/owner_dashboard.html', 'templates/dashboard/owner_dashboard.html'),
    ('templates/dashboard/owner_services.html', 'templates/dashboard/owner_services.html'),
    ('templates/dashboard/owner_employees.html', 'templates/dashboard/owner_employees.html'),
    ('templates/dashboard/owner_settings.html', 'templates/dashboard/owner_settings.html'),
    ('templates/dashboard/schedule_row.html', 'templates/dashboard/schedule_row.html'),
    ('templates/dashboard/service_form.html', 'templates/dashboard/service_form.html'),
    ('templates/dashboard/employee_form.html', 'templates/dashboard/employee_form.html'),
]

def main():
    print("⛑️  INICIANDO OPERACIÓN DE RESCATE DESDE BACKUP...")
    
    # 1. Verificar que el backup existe
    if not os.path.exists(BACKUP_DIR):
        print(f"❌ ERROR: No encuentro la carpeta '{BACKUP_DIR}' en este directorio.")
        print("   Asegúrate de haber descomprimido o movido la carpeta 'pasofinalbacukp' aquí.")
        return

    # 2. Ejecutar Copia
    count = 0
    for src_rel, dest_rel in FILE_MAPPING:
        src_path = os.path.join(BACKUP_DIR, src_rel)
        dest_path = os.path.join(os.getcwd(), dest_rel)

        if os.path.exists(src_path):
            try:
                # Crear carpetas si no existen
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                # Copiar archivo
                shutil.copy2(src_path, dest_path)
                print(f"✅ Recuperado: {src_rel} -> {dest_rel}")
                count += 1
            except Exception as e:
                print(f"⚠️ Error copiando {src_rel}: {e}")
        else:
            print(f"❓ No encontrado en backup: {src_rel} (Se omitió)")

    # 3. Finalización
    if count > 0:
        print(f"\n✨ ¡ÉXITO! Se han recuperado {count} archivos clave.")
        print("👉 Siguientes pasos:")
        print("   1. Ejecuta: python manage.py migrate (Por si el models.py trajo cambios)")
        print("   2. Ejecuta: git add .")
        print("   3. Ejecuta: git commit -m 'Restored owner panel from backup'")
        print("   4. Ejecuta: git push origin main")
    else:
        print("\n⚠️ No se pudo recuperar ningún archivo. Verifica la estructura del backup.")

if __name__ == "__main__":
    main()