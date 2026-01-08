import os
import shutil

def fix_folders():
    print("🚑 INICIANDO REPARACIÓN DE ESTRUCTURA DE CARPETAS...")

    base_dir = os.getcwd()
    apps_dir = os.path.join(base_dir, 'apps')
    core_dir = os.path.join(apps_dir, 'core')
    core_saas_dir = os.path.join(apps_dir, 'core_saas')

    # 1. RENOMBRAR CARPETA 'core' -> 'core_saas'
    if os.path.exists(core_dir):
        if os.path.exists(core_saas_dir):
            print("⚠️ Ambas carpetas existen ('core' y 'core_saas'). Fusionando contenido...")
            # Mover contenido de core a core_saas
            for item in os.listdir(core_dir):
                s = os.path.join(core_dir, item)
                d = os.path.join(core_saas_dir, item)
                if os.path.exists(d):
                    if os.path.isdir(d):
                        pass # Si es directorio y existe, lo dejamos (se asume merge manual si fuera necesario)
                    else:
                        os.remove(d) # Si es archivo, sobrescribimos
                        shutil.move(s, d)
                else:
                    shutil.move(s, d)
            # Eliminar core vacía
            shutil.rmtree(core_dir)
            print("✅ Contenido de 'apps/core' movido a 'apps/core_saas'. Carpeta 'apps/core' eliminada.")
        else:
            os.rename(core_dir, core_saas_dir)
            print("✅ Carpeta renombrada: 'apps/core' -> 'apps/core_saas'")
    elif os.path.exists(core_saas_dir):
        print("✅ La carpeta 'apps/core_saas' ya existe. No se requiere renombrar.")
    else:
        print("❌ ERROR CRÍTICO: No se encontró ni 'apps/core' ni 'apps/core_saas'.")
        return

    # 2. CORREGIR URLS.PY (Actualizar referencia)
    # Buscamos en las ubicaciones probables del archivo de URLs principal
    urls_locations = [
        os.path.join(base_dir, 'paso_ecosystem', 'urls.py'),
        os.path.join(base_dir, 'config', 'urls.py'),
    ]
    
    urls_fixed = False
    for url_path in urls_locations:
        if os.path.exists(url_path):
            with open(url_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'apps.core_saas.urls' in content:
                new_content = content.replace('apps.core_saas.urls', 'apps.core_saas.urls')
                with open(url_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Referencia corregida en: {url_path}")
                urls_fixed = True
            elif 'apps.core_saas.urls' in content:
                 print(f"✅ {url_path} ya apunta correctamente a 'apps.core_saas.urls'.")
                 urls_fixed = True
    
    if not urls_fixed:
        print("⚠️ No se encontró ningún archivo urls.py principal o no necesitaba cambios.")

    # 3. VERIFICAR APPS.PY (Configuración de la App)
    apps_py_path = os.path.join(core_saas_dir, 'apps.py')
    if os.path.exists(apps_py_path):
        with open(apps_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Asegurar que el name sea correcto
        if "name = 'apps.core'" in content:
            new_content = content.replace("name = 'apps.core'", "name = 'apps.core_saas'")
            with open(apps_py_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ apps.core_saas/apps.py actualizado (name = 'apps.core_saas').")
        elif "name = 'core'" in content: # Caso viejo
             new_content = content.replace("name = 'core'", "name = 'apps.core_saas'")
             with open(apps_py_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
             print("✅ apps.core_saas/apps.py actualizado (name = 'apps.core_saas').")

    print("\n✨ ESTRUCTURA CORREGIDA ✨")
    print("Ahora ejecuta estos comandos para actualizar Git:")
    print("1. git add .")
    print("2. git commit -m 'Fix: Rename core app to core_saas'")
    print("3. git push origin main")

if __name__ == "__main__":
    fix_folders()