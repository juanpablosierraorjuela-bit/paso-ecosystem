import os

# ==========================================
# SOLUCIÓN: APPS/BUSINESSES/URLS.PY
# ==========================================
# Basado en tus archivos:
# - views.owner_dashboard (Existe) -> Usaremos para 'dashboard'
# - views.services_list (Existe) -> Usaremos para 'services'
# - views.schedule_config (Existe) -> Usaremos para 'schedule' (antes schedule_list)
# - views.employees_list (Existe) -> Usaremos para 'employees'
# - views.business_settings (Existe) -> Usaremos para 'settings'

urls_content = """from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    # 1. Dashboard Principal (Tu vista se llama owner_dashboard)
    path('dashboard/', views.owner_dashboard, name='dashboard'),
    
    # 2. Servicios
    path('services/', views.services_list, name='services'),
    
    # 3. Horarios (CORREGIDO: schedule_config en lugar de schedule_list)
    path('schedule/', views.schedule_config, name='schedule'),
    
    # 4. Empleados (Faltaba en tu archivo anterior)
    path('employees/', views.employees_list, name='employees'),
    
    # 5. Configuración (Faltaba en tu archivo anterior)
    path('settings/', views.business_settings, name='settings'),
    
    # Ruta 'panel' redirigida al dashboard para compatibilidad
    path('panel/', views.owner_dashboard, name='panel_negocio'),
]
"""

def main():
    path_url = 'apps/businesses/urls.py'
    print(f"🔗 REPARANDO RUTAS EN {path_url}...")
    
    try:
        os.makedirs(os.path.dirname(path_url), exist_ok=True)
        with open(path_url, 'w', encoding='utf-8') as f:
            f.write(urls_content)
            
        print("✅ urls.py ha sido corregido.")
        print("   - Se corrigió 'schedule_list' -> 'schedule_config'")
        print("   - Se agregaron las rutas faltantes 'employees' y 'settings'")
        
        print("\n👉 EJECUTA ESTO EN LA TERMINAL:")
        print("   python manage.py migrate  (Para asegurar la base de datos)")
        print("   git add .")
        print("   git commit -m 'Fix: Rutas corregidas y alineadas con views.py'")
        print("   git push origin main")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()