import os
import subprocess
import sys

def reparar_urls_negocio():
    print("🔗 SINCRONIZANDO URLS DE NEGOCIOS...")

    # 1. REESCRIBIR APPS/BUSINESSES/URLS.PY
    # Este archivo conectará exactamente con los nombres de funciones que existen en views.py
    urls_path = os.path.join('apps', 'businesses', 'urls.py')
    
    urls_content = """from django.urls import path
from . import views

urlpatterns = [
    # --- DASHBOARD DUEÑO ---
    path('dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('configuracion/', views.owner_settings, name='owner_settings'),
    
    # --- GESTIÓN DE SERVICIOS ---
    # Aquí estaba el error: antes buscaba 'services_list', ahora apunta a 'owner_services'
    path('servicios/', views.owner_services, name='owner_services'), 
    path('servicios/crear/', views.service_create, name='service_create'),
    path('servicios/editar/<int:pk>/', views.service_update, name='service_update'),
    path('servicios/eliminar/<int:pk>/', views.service_delete, name='service_delete'),
    
    # --- GESTIÓN DE EMPLEADOS ---
    path('empleados/', views.owner_employees, name='owner_employees'),
    path('empleados/crear/', views.employee_create, name='employee_create'),
    path('empleados/editar/<int:pk>/', views.employee_update, name='employee_update'),
    path('empleados/eliminar/<int:pk>/', views.employee_delete, name='employee_delete'),
    
    # --- DASHBOARD EMPLEADO ---
    path('mi-agenda/', views.employee_dashboard, name='employee_dashboard'),
    path('mi-horario/', views.employee_schedule, name='employee_schedule'),
    
    # --- VERIFICACIÓN DE CITAS ---
    path('citas/verificar/<int:pk>/', views.verify_booking, name='verify_booking'),
]
"""

    os.makedirs(os.path.dirname(urls_path), exist_ok=True)
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_content)
    print("✅ apps/businesses/urls.py actualizado y sincronizado.")

    # 2. REINTENTAR MIGRACIONES (AHORA SÍ DEBERÍA PASAR)
    print("\n✨ Ejecutando makemigrations...")
    try:
        subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'core_saas', 'businesses'], check=True)
        print("✅ ¡MIGRACIONES ÉXITOSAS!")
        
        print("📥 Migrando DB local...")
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("✅ DB Local lista y operativa.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return

    print("\n🚀 ¡SISTEMA COMPLETAMENTE OPERATIVO!")
    print("Por favor, sube estos cambios ya mismo:")
    print("---------------------------------------------------")
    print("git add .")
    print("git commit -m \"Final Fix: Sync URLs with Views in businesses app\"")
    print("git push origin main")
    print("---------------------------------------------------")

if __name__ == "__main__":
    reparar_urls_negocio()