import os

def completar_urls_negocio():
    print("🔗 RESTAURANDO RUTAS PERDIDAS DEL WIZARD DE RESERVAS...")

    urls_path = os.path.join('apps', 'businesses', 'urls.py')
    
    # Agregamos TODAS las rutas, incluyendo las del flujo de reserva que faltaban
    urls_content = """from django.urls import path
from . import views

urlpatterns = [
    # --- DASHBOARD DUEÑO ---
    path('dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('configuracion/', views.owner_settings, name='owner_settings'),
    
    # --- GESTIÓN DE SERVICIOS ---
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

    # --- WIZARD DE RESERVAS (ESTAS ERAN LAS QUE FALTABAN) ---
    path('reserva/inicio/', views.booking_wizard_start, name='booking_wizard_start'),
    path('reserva/profesional/', views.booking_step_employee, name='booking_step_employee'),
    path('reserva/calendario/', views.booking_step_calendar, name='booking_step_calendar'),
    path('reserva/confirmar/', views.booking_step_confirm, name='booking_step_confirm'),
    path('reserva/crear/', views.booking_create, name='booking_create_internal'),
]
"""

    os.makedirs(os.path.dirname(urls_path), exist_ok=True)
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_content)
    print("✅ apps/businesses/urls.py completado con éxito.")
    
    # TAMBIÉN ASEGURAMOS SETTINGS.PY PARA QUE NO FALLE POR HOSTS
    print("🛡️ Asegurando ALLOWED_HOSTS en settings.py...")
    try:
        settings_path = os.path.join('config', 'settings.py')
        if not os.path.exists(settings_path):
             settings_path = os.path.join('paso_ecosystem', 'settings.py')
             
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Forzamos aceptar todo en Render para descartar error 400/500 por dominio
        if "ALLOWED_HOSTS =" in content:
            # Reemplazo simple y bruto para asegurar que funcione
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.strip().startswith("ALLOWED_HOSTS"):
                    new_lines.append("ALLOWED_HOSTS = ['*']  # Fix temporal para Render")
                else:
                    new_lines.append(line)
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            print("✅ ALLOWED_HOSTS configurado a ['*'].")
    except Exception as e:
        print(f"⚠️ No pude editar settings.py: {e}")

    print("\n🚀 LISTO. EJECUTA LOS COMANDOS DE GIT:")
    print("1. git add .")
    print("2. git commit -m \"Fix: Restore missing booking URLs and permissive hosts\"")
    print("3. git push origin main")

if __name__ == "__main__":
    completar_urls_negocio()