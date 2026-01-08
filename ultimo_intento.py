import os

def forzar_correccion():
    print("🕵️ DIAGNOSTICANDO ARCHIVO APPS.PY ...")
    
    # Ruta del archivo problemático
    ruta_apps = os.path.join('apps', 'core_saas', 'apps.py')
    ruta_init = os.path.join('apps', 'core_saas', '__init__.py')
    
    # 1. VERIFICAR SI EXISTE LA CARPETA
    if not os.path.exists(os.path.dirname(ruta_apps)):
        print(f"❌ ERROR: La carpeta {os.path.dirname(ruta_apps)} no existe.")
        print("Asegúrate de haber ejecutado 'fix_folders.py' primero.")
        return

    # 2. SOBRESCRIBIR APPS.PY CON EL CÓDIGO CORRECTO
    contenido_correcto = """from django.apps import AppConfig

class CoreSaasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core_saas'
    label = 'core_saas'
"""
    try:
        with open(ruta_apps, 'w', encoding='utf-8') as f:
            f.write(contenido_correcto)
        print(f"✅ ¡CORREGIDO! Se ha reescrito {ruta_apps}")
        print("   Ahora contiene: name = 'apps.core_saas'")
    except Exception as e:
        print(f"❌ No se pudo escribir el archivo: {e}")

    # 3. LIMPIAR __INIT__.PY (Para evitar conflictos fantasmas)
    try:
        with open(ruta_init, 'w', encoding='utf-8') as f:
            f.write("")
        print(f"✅ LIMPIO: {ruta_init} ahora está vacío.")
    except Exception as e:
        print(f"⚠️ No se pudo limpiar __init__.py: {e}")

    # 4. VERIFICAR SETTINGS.PY (Doble chequeo)
    try:
        if os.path.exists('paso_ecosystem/settings.py'):
            ruta_settings = 'paso_ecosystem/settings.py'
        else:
            ruta_settings = 'config/settings.py'
            
        with open(ruta_settings, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "'apps.core_saas'" in content or '"apps.core_saas"' in content:
            print("✅ SETTINGS: INSTALLED_APPS ya tiene 'apps.core_saas'.")
        else:
            print("❌ SETTINGS: ¡ALERTA! No veo 'apps.core_saas' en settings.py.")
    except:
        pass

    print("\n🏁 PROCESO TERMINADO. IMPORTANTE:")
    print("Debes ejecutar estos comandos EXACTOS en tu terminal para que Render reciba el cambio:")
    print("---------------------------------------------------")
    print("git add .")
    print("git commit -m \"Fix: Force CoreSaasConfig name in apps.py\"")
    print("git push origin main")
    print("---------------------------------------------------")

if __name__ == "__main__":
    forzar_correccion()