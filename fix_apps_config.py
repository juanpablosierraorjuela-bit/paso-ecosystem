import os

def fix_apps_config():
    print("🚑 REPARANDO CONFIGURACIÓN DE APPS (FUERZA BRUTA)...")
    
    # 1. REESCRIBIR APPS/CORE_SAAS/APPS.PY
    # Aseguramos que la clase se llame CoreSaasConfig y el name sea 'apps.core_saas'
    core_apps_path = os.path.join('apps', 'core_saas', 'apps.py')
    core_apps_content = """from django.apps import AppConfig

class CoreSaasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core_saas'
    label = 'core_saas'
"""
    try:
        os.makedirs(os.path.dirname(core_apps_path), exist_ok=True)
        with open(core_apps_path, 'w', encoding='utf-8') as f:
            f.write(core_apps_content)
        print(f"✅ Reescribiendo {core_apps_path} con configuración correcta.")
    except Exception as e:
        print(f"❌ Error escribiendo {core_apps_path}: {e}")

    # 2. LIMPIAR APPS/CORE_SAAS/__INIT__.PY
    # A veces este archivo tiene "default_app_config" apuntando a la clase vieja. Lo limpiamos.
    core_init_path = os.path.join('apps', 'core_saas', '__init__.py')
    try:
        with open(core_init_path, 'w', encoding='utf-8') as f:
            f.write("") # Archivo vacío
        print(f"✅ Limpiando {core_init_path} para evitar conflictos antiguos.")
    except Exception as e:
        print(f"❌ Error limpiando {core_init_path}: {e}")

    # 3. VERIFICAR APPS/BUSINESSES/APPS.PY
    # Solo por seguridad, reescribimos este también.
    biz_apps_path = os.path.join('apps', 'businesses', 'apps.py')
    biz_apps_content = """from django.apps import AppConfig

class BusinessesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.businesses'
"""
    try:
        os.makedirs(os.path.dirname(biz_apps_path), exist_ok=True)
        with open(biz_apps_path, 'w', encoding='utf-8') as f:
            f.write(biz_apps_content)
        print(f"✅ Reescribiendo {biz_apps_path} para asegurar integridad.")
    except Exception as e:
        print(f"❌ Error escribiendo {biz_apps_path}: {e}")

    print("\n✨ REPARACIÓN COMPLETADA ✨")
    print("Ahora ejecuta estos comandos para enviar los cambios:")
    print("1. git add .")
    print("2. git commit -m 'Fix: Rewrite AppConfig to force apps.core_saas name'")
    print("3. git push origin main")

if __name__ == "__main__":
    fix_apps_config()