import os

def sincronizar_referencias():
    print("🔄 SINCRONIZANDO REFERENCIAS: APPS.CORE -> APPS.CORE_SAAS ...")

    # 1. VERIFICAR QUE LA CARPETA EXISTA
    if os.path.exists(os.path.join('apps', 'core_saas')):
        print("✅ Carpeta 'apps/core_saas' detectada correctamente.")
    elif os.path.exists(os.path.join('apps', 'core')):
        print("⚠️ PRECAUCIÓN: Todavía existe 'apps/core'. Asegúrate de haber ejecutado el script anterior 'fix_folders.py'.")
    
    # 2. LISTA DE ARCHIVOS CLAVE A REVISAR
    # Revisaremos settings.py, urls.py y todos los archivos .py dentro de las apps
    archivos_modificados = 0
    
    for root, dirs, files in os.walk('.'):
        # Ignorar carpetas del sistema
        if '.venv' in root or '.git' in root or '__pycache__' in root or 'migrations' in root:
            continue
            
        for file in files:
            if file.endswith('.py') or file.endswith('.html'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    
                    new_content = original_content
                    
                    # --- REEMPLAZOS CLAVE ---
                    # 1. En settings.py: INSTALLED_APPS
                    if file == 'settings.py':
                        new_content = new_content.replace("'apps.core'", "'apps.core_saas'")
                        new_content = new_content.replace('"apps.core"', '"apps.core_saas"')
                    
                    # 2. Imports en Python
                    new_content = new_content.replace("from apps.core_saas ", "from apps.core_saas ")
                    new_content = new_content.replace("from apps.core_saas.", "from apps.core_saas.")
                    new_content = new_content.replace("import apps.core_saas", "import apps.core_saas_saas")
                    
                    # 3. Referencias en URLs (strings)
                    new_content = new_content.replace("apps.core_saas.urls", "apps.core_saas.urls")
                    
                    # 4. AppsConfig (apps.py)
                    if file == 'apps.py' and "name = 'apps.core'" in new_content:
                        new_content = new_content.replace("name = 'apps.core'", "name = 'apps.core_saas'")

                    # --- GUARDAR SI HUBO CAMBIOS ---
                    if new_content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"🔧 Corregido: {file_path}")
                        archivos_modificados += 1
                        
                except Exception as e:
                    print(f"❌ Error leyendo {file_path}: {e}")

    print(f"\n✨ Proceso terminado. Archivos corregidos: {archivos_modificados}")
    
    if archivos_modificados > 0:
        print("\n⚠️ IMPORTANTE: Ejecuta estos comandos ahora:")
        print("1. git add .")
        print("2. git commit -m 'Fix: Update all references to apps.core_saas'")
        print("3. git push origin main")
    else:
        print("\n✅ Todo parece estar en orden. Si el error persiste, verifica manualmente 'paso_ecosystem/settings.py'.")

if __name__ == "__main__":
    sincronizar_referencias()